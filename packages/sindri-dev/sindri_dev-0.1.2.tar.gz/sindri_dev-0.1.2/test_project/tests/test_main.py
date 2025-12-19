"""Tests for main module."""

from typer.testing import CliRunner

from test_project.main import app


def test_hello_command() -> None:
    """Test hello command."""
    runner = CliRunner()
    result = runner.invoke(app, ["hello", "Test"])
    assert result.exit_code == 0
    assert "Hello, Test!" in result.stdout


def test_hello_default() -> None:
    """Test hello command with default name."""
    runner = CliRunner()
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout


def test_version_command() -> None:
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "test-project" in result.stdout
    assert "0.1.0" in result.stdout

