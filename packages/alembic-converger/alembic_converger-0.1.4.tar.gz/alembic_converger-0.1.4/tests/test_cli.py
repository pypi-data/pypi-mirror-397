"""
Tests for CLI module.
"""

from click.testing import CliRunner

from alembic_converger.cli import cli


class TestCLI:
    """Test CLI interface."""

    def test_version_option(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "alembic-converger" in result.output

    def test_help_output(self):
        """Test help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Alembic Converger" in result.output

    def test_converge_help(self):
        """Test converge command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["converge", "--help"])
        assert result.exit_code == 0
        assert "--from-revision" in result.output
        assert "--dry-run" in result.output
        assert "--skip-validation" in result.output

    def test_converge_requires_from_revision(self):
        """Test that converge command requires --from-revision."""
        runner = CliRunner()
        result = runner.invoke(cli, ["converge"])
        assert result.exit_code != 0
        assert (
            "from-revision" in result.output.lower()
            or "missing" in result.output.lower()
        )

    def test_converge_missing_config_file(self):
        """Test error when config file is missing."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "converge",
                "--from-revision",
                "abc123",
                "--alembic-config",
                "/nonexistent/alembic.ini",
            ],
        )
        assert result.exit_code == 2  # Configuration error
