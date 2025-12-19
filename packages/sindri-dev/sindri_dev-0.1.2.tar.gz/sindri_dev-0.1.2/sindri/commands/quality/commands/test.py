"""Test command."""

from sindri.commands.shell_command import ShellCommand


class TestCommand(ShellCommand):
    """Run tests command."""

    def __init__(self):
        super().__init__(
            command_id="test",
            shell="pytest",
            title="Test",
            description="Run tests",
        )

