"""
Simplified Windows persistent terminal using PowerShell subprocess (persistent).
Binary stdout + incremental decode to support reliable streaming without hangs.

Includes:
- execute_command(...)
- execute_command_streaming(..., callback=...)
"""

import os
import time
import random
import subprocess
import ctypes
import msvcrt
import codecs
from dataclasses import dataclass
from typing import Optional, Callable
from ctypes import wintypes


@dataclass
class TerminalResult:
    command: str
    output: str
    return_code: int
    execution_time: float


class TerminalSessionError(Exception):
    pass


# --- Win32 PeekNamedPipe plumbing (non-blocking “how many bytes available?”) ---
_KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
_PeekNamedPipe = _KERNEL32.PeekNamedPipe
_PeekNamedPipe.argtypes = [
    wintypes.HANDLE,                 # hNamedPipe
    wintypes.LPVOID,                 # lpBuffer
    wintypes.DWORD,                  # nBufferSize
    ctypes.POINTER(wintypes.DWORD),  # lpBytesRead
    ctypes.POINTER(wintypes.DWORD),  # lpTotalBytesAvail
    ctypes.POINTER(wintypes.DWORD),  # lpBytesLeftThisMessage
]
_PeekNamedPipe.restype = wintypes.BOOL


class PersistentTerminal:
    def __init__(self):
        self._proc: Optional[subprocess.Popen] = None
        self._working_directory: Optional[str] = None

    def start_session(self, working_dir: str) -> None:
        """Start a persistent PowerShell process."""
        if self._proc:
            self.close()

        working_dir = os.path.abspath(working_dir)
        if not os.path.exists(working_dir):
            raise TerminalSessionError(f"Working directory does not exist: {working_dir}")

        ps_exe = "pwsh" if self._has_pwsh() else "powershell"

        try:
            # IMPORTANT: text=False => binary pipes (prevents byte/char mismatch hangs)
            self._proc = subprocess.Popen(
                [ps_exe, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "-"],
                cwd=working_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,        # <-- binary!
                bufsize=0,         # unbuffered in Python
            )
            self._working_directory = working_dir
        except Exception as e:
            raise TerminalSessionError(f"Failed to start PowerShell session: {e}")

    def _has_pwsh(self) -> bool:
        """Detect PowerShell 7 (pwsh) if present."""
        try:
            subprocess.run(["pwsh", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def is_alive(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def _peek_available_bytes(self, hpipe: wintypes.HANDLE) -> int:
        total_avail = wintypes.DWORD(0)
        ok = _PeekNamedPipe(hpipe, None, 0, None, ctypes.byref(total_avail), None)
        if not ok:
            return 0
        return int(total_avail.value)

    def execute_command(self, command: str, timeout: int = 30) -> TerminalResult:
        """Execute a command and return its output and exit code (non-streaming)."""
        if not self.is_alive():
            raise TerminalSessionError("No active PowerShell session.")
        assert self._proc and self._proc.stdin and self._proc.stdout

        start = time.time()
        salt = str(random.randint(100000, 999999))
        end_marker = f"__ORCH_END__{salt}"
        rc_marker = f"__ORCH_RC__{salt}"

        # Add flushes to reduce the chance of marker buffering
        ps_script = (
            f"{command}\n"
            f"$code = if ($LASTEXITCODE) {{ $LASTEXITCODE }} elseif ($?) {{ 0 }} else {{ 1 }}\n"
            f"Write-Output '{rc_marker}:$code'\n"
            f"Write-Output '{end_marker}'\n"
            f"[Console]::Out.Flush()\n"
        )

        # Send script
        self._proc.stdin.write(ps_script.encode("utf-8", errors="replace"))
        self._proc.stdin.flush()

        # Setup non-blocking reads
        fd = self._proc.stdout.fileno()
        os_handle = msvcrt.get_osfhandle(fd)
        hpipe = wintypes.HANDLE(os_handle)

        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        text_buf = ""
        out_lines: list[str] = []
        return_code = 0

        deadline = start + timeout

        while True:
            if time.time() > deadline:
                partial = "\n".join(out_lines)
                raise TerminalSessionError(
                    f"Command timed out after {timeout}s: {command}\nPartial output: {partial[:500]}"
                )

            if self._proc.poll() is not None:
                partial = "\n".join(out_lines)
                raise TerminalSessionError(
                    "PowerShell session terminated unexpectedly.\n"
                    f"Partial output: {partial[:500]}"
                )

            avail = self._peek_available_bytes(hpipe)
            if avail <= 0:
                time.sleep(0.01)
                continue

            data = os.read(fd, min(avail, 65536))
            if not data:
                time.sleep(0.01)
                continue

            text_buf += decoder.decode(data)

            # Parse by lines, but also handle markers even if not line-terminated
            while True:
                # If end marker appears anywhere, we can finish.
                end_idx = text_buf.find(end_marker)
                if end_idx != -1:
                    before_end = text_buf[:end_idx]
                    # Consume up to (and including) end marker (and optional trailing newline)
                    after_end = text_buf[end_idx + len(end_marker):]
                    # Remove a leading newline after marker if present
                    if after_end.startswith("\r\n"):
                        after_end = after_end[2:]
                    elif after_end.startswith("\n") or after_end.startswith("\r"):
                        after_end = after_end[1:]
                    text_buf = after_end

                    # Process whatever was before end marker line-wise
                    for raw_line in before_end.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
                        if not raw_line:
                            continue
                        if raw_line.startswith(rc_marker + ":"):
                            try:
                                return_code = int(raw_line.split(":", 1)[1])
                            except Exception:
                                return_code = 0
                        else:
                            out_lines.append(raw_line)
                    output = "\n".join(out_lines).strip()
                    elapsed = time.time() - start
                    return TerminalResult(command, output, return_code, elapsed)

                # Otherwise, extract complete lines only
                nl = text_buf.find("\n")
                cr = text_buf.find("\r")
                cut = -1
                if nl != -1 and cr != -1:
                    cut = min(nl, cr)
                else:
                    cut = nl if nl != -1 else cr

                if cut == -1:
                    break

                line = text_buf[:cut]
                # consume newline char(s)
                text_buf = text_buf[cut + 1 :]
                if text_buf.startswith("\n") and line.endswith("\r"):
                    # rare double consume case; safe no-op
                    pass

                line = line.rstrip("\r\n")
                if not line:
                    continue
                if line.startswith(rc_marker + ":"):
                    try:
                        return_code = int(line.split(":", 1)[1])
                    except Exception:
                        return_code = 0
                elif line == end_marker:
                    output = "\n".join(out_lines).strip()
                    elapsed = time.time() - start
                    return TerminalResult(command, output, return_code, elapsed)
                else:
                    out_lines.append(line)

    def execute_command_streaming(
        self,
        command: str,
        timeout: int = 30,
        callback: Optional[Callable[[str], None]] = None,
        poll_interval: float = 0.01,
        read_chunk_size: int = 65536,
    ) -> TerminalResult:
        """
        Execute a command and stream output to callback as it arrives.

        callback receives *text chunks* (often line-ish, but not guaranteed).
        """
        if not self.is_alive():
            raise TerminalSessionError("No active PowerShell session.")
        assert self._proc and self._proc.stdin and self._proc.stdout

        start = time.time()
        salt = str(random.randint(100000, 999999))
        end_marker = f"__ORCH_END__{salt}"
        rc_marker = f"__ORCH_RC__{salt}"

        ps_script = (
            f"{command}\n"
            f"$code = if ($LASTEXITCODE) {{ $LASTEXITCODE }} elseif ($?) {{ 0 }} else {{ 1 }}\n"
            f"Write-Output '{rc_marker}:$code'\n"
            f"Write-Output '{end_marker}'\n"
            f"[Console]::Out.Flush()\n"
        )

        # Send script
        self._proc.stdin.write(ps_script.encode("utf-8", errors="replace"))
        self._proc.stdin.flush()

        fd = self._proc.stdout.fileno()
        os_handle = msvcrt.get_osfhandle(fd)
        hpipe = wintypes.HANDLE(os_handle)

        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        text_buf = ""
        output_accum: list[str] = []
        return_code = 0
        deadline = start + timeout

        def emit(s: str) -> None:
            if not s:
                return
            output_accum.append(s)
            if callback:
                try:
                    callback(s)
                except Exception as e:
                    raise TerminalSessionError(f"Streaming callback raised: {e}")

        while True:
            if time.time() > deadline:
                partial = "".join(output_accum)
                raise TerminalSessionError(
                    f"Command timed out after {timeout}s: {command}\nPartial output: {partial[:500]}"
                )

            if self._proc.poll() is not None:
                partial = "".join(output_accum)
                raise TerminalSessionError(
                    "PowerShell session terminated unexpectedly.\n"
                    f"Partial output: {partial[:500]}"
                )

            avail = self._peek_available_bytes(hpipe)
            if avail <= 0:
                time.sleep(poll_interval)
                continue

            data = os.read(fd, min(avail, read_chunk_size))
            if not data:
                time.sleep(poll_interval)
                continue

            text_buf += decoder.decode(data)

            # If end marker appears anywhere, finish (even without newline).
            end_idx = text_buf.find(end_marker)
            if end_idx != -1:
                before_end = text_buf[:end_idx]
                after_end = text_buf[end_idx + len(end_marker):]
                text_buf = after_end  # leftover (usually empty)

                # Process "before_end": stream everything except rc line
                normalized = before_end.replace("\r\n", "\n").replace("\r", "\n")
                for line in normalized.split("\n"):
                    if not line:
                        continue
                    if line.startswith(rc_marker + ":"):
                        try:
                            return_code = int(line.split(":", 1)[1])
                        except Exception:
                            return_code = 0
                    else:
                        emit(line + "\n")

                # done
                output = "".join(output_accum).replace("\r\n", "\n").replace("\r", "\n").strip()
                elapsed = time.time() - start
                return TerminalResult(command, output, return_code, elapsed)

            # Otherwise, stream complete lines as they become available
            while True:
                # Find earliest line break
                nl = text_buf.find("\n")
                cr = text_buf.find("\r")
                cut = -1
                if nl != -1 and cr != -1:
                    cut = min(nl, cr)
                else:
                    cut = nl if nl != -1 else cr

                if cut == -1:
                    break

                line = text_buf[:cut]
                text_buf = text_buf[cut + 1 :]

                line = line.rstrip("\r\n")
                if not line:
                    continue
                if line.startswith(rc_marker + ":"):
                    try:
                        return_code = int(line.split(":", 1)[1])
                    except Exception:
                        return_code = 0
                    continue
                if line == end_marker:
                    output = "".join(output_accum).replace("\r\n", "\n").replace("\r", "\n").strip()
                    elapsed = time.time() - start
                    return TerminalResult(command, output, return_code, elapsed)

                emit(line + "\n")

    def restart_session(self, working_dir: Optional[str] = None) -> None:
        """Restart the PowerShell session."""
        if working_dir is None:
            working_dir = self._working_directory
        if not working_dir:
            raise TerminalSessionError("No working directory specified for restart")
        self.close()
        self.start_session(working_dir)

    def close(self) -> None:
        """Gracefully close the PowerShell session."""
        if self._proc:
            try:
                if self._proc.stdin:
                    self._proc.stdin.write(b"exit\n")
                    self._proc.stdin.flush()
            except Exception:
                pass
            try:
                self._proc.terminate()
            except Exception:
                pass
            try:
                self._proc.wait(timeout=2)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
        self._proc = None

    def __del__(self):
        self.close()
