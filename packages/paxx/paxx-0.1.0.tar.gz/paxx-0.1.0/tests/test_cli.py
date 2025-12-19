"""Tests for the paxx CLI."""

from typer.testing import CliRunner

from paxx.cli.main import app

runner = CliRunner()


def test_version_flag():
    """Test that the --version flag outputs the version."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "paxx version" in result.stdout


def test_version_flag_short():
    """Test that the -v flag outputs the version."""
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    assert "paxx version" in result.stdout


def test_help():
    """Test that --help shows help text."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "paxx" in result.stdout
