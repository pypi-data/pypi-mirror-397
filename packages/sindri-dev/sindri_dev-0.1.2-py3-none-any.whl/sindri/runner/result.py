"""Command execution result."""

from typing import Optional


class CommandResult:
    """Result of a command execution."""

    def __init__(
        self,
        command_id: str,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        duration: float = 0.0,
        error: Optional[str] = None,
    ):
        self.command_id = command_id
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration = duration
        self.error = error
        self.success = exit_code == 0

    def __repr__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"CommandResult({self.command_id}, {status}, exit_code={self.exit_code})"

