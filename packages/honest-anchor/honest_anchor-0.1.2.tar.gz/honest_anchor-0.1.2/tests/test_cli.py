"""
Unit tests for Honest Anchor CLI.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from honest_anchor.cli import (
    cli,
    sha256_file,
    load_registry,
    save_registry,
    get_anchor_dir,
    get_staged_files,
    ANCHOR_DIR,
    REGISTRY_FILE,
    PROOFS_DIR,
)


class TestSha256File:
    """Tests for sha256_file function."""

    def test_sha256_file_basic(self, tmp_path):
        """Test basic hash calculation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        result = sha256_file(test_file)

        assert len(result) == 64  # SHA256 produces 64 hex chars
        assert result == "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"

    def test_sha256_file_empty(self, tmp_path):
        """Test hash of empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        result = sha256_file(test_file)

        # SHA256 of empty string
        assert result == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_sha256_file_binary(self, tmp_path):
        """Test hash of binary file."""
        test_file = tmp_path / "binary.bin"
        test_file.write_bytes(b"\x00\x01\x02\x03")

        result = sha256_file(test_file)

        assert len(result) == 64


class TestRegistry:
    """Tests for registry functions."""

    def test_load_registry_not_exists(self, tmp_path):
        """Test loading registry when file doesn't exist."""
        result = load_registry(tmp_path)

        assert result == {"files": {}, "version": "1.0"}

    def test_load_registry_exists(self, tmp_path):
        """Test loading existing registry."""
        registry_data = {"files": {"test.py": {"hash": "abc123"}}, "version": "1.0"}
        registry_file = tmp_path / REGISTRY_FILE
        registry_file.write_text(json.dumps(registry_data))

        result = load_registry(tmp_path)

        assert result == registry_data

    def test_save_registry(self, tmp_path):
        """Test saving registry."""
        registry_data = {"files": {"test.py": {"hash": "abc123"}}, "version": "1.0"}

        save_registry(tmp_path, registry_data)

        registry_file = tmp_path / REGISTRY_FILE
        assert registry_file.exists()
        loaded = json.loads(registry_file.read_text())
        assert loaded == registry_data


class TestCliInit:
    """Tests for anchor init command."""

    def test_init_creates_directory(self, tmp_path):
        """Test that init creates .anchor directory."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ['init'])

            assert result.exit_code == 0
            assert Path(ANCHOR_DIR).exists()
            assert (Path(ANCHOR_DIR) / PROOFS_DIR).exists()
            assert (Path(ANCHOR_DIR) / "config.yml").exists()
            assert (Path(ANCHOR_DIR) / REGISTRY_FILE).exists()

    def test_init_already_exists(self, tmp_path):
        """Test init when .anchor already exists."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path(ANCHOR_DIR).mkdir()
            result = runner.invoke(cli, ['init'])

            assert "already exists" in result.output


class TestCliCommit:
    """Tests for anchor commit command."""

    def test_commit_no_init(self, tmp_path):
        """Test commit without init."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("test.py").write_text("print('hello')")
            result = runner.invoke(cli, ['commit', 'test.py'])

            assert result.exit_code == 1
            assert "init" in result.output.lower()

    @patch('honest_anchor.cli.run_ots_command')
    def test_commit_success(self, mock_ots, tmp_path):
        """Test successful commit."""
        mock_ots.return_value = (True, "Success")
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Init first
            runner.invoke(cli, ['init'])

            # Create test file
            Path("test.py").write_text("print('hello')")

            # Create fake .ots file that OTS would create
            Path("test.py.ots").write_bytes(b"fake ots proof")

            result = runner.invoke(cli, ['commit', 'test.py'])

            assert "Anchoring" in result.output or "Submitted" in result.output


class TestCliStatus:
    """Tests for anchor status command."""

    def test_status_no_files(self, tmp_path):
        """Test status with no anchored files."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(cli, ['init'])
            result = runner.invoke(cli, ['status'])

            assert "No files anchored" in result.output or result.exit_code == 0


class TestCliVerify:
    """Tests for anchor verify command."""

    def test_verify_not_anchored(self, tmp_path):
        """Test verify for non-anchored file."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(cli, ['init'])
            Path("test.py").write_text("print('hello')")

            result = runner.invoke(cli, ['verify', 'test.py'])

            assert result.exit_code == 1
            assert "not anchored" in result.output.lower()


class TestCliHelp:
    """Tests for CLI help."""

    def test_help(self):
        """Test --help flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert "Honest Anchor" in result.output
        assert "commit" in result.output
        assert "init" in result.output

    def test_version(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])

        assert result.exit_code == 0
        assert "0.1.1" in result.output


class TestGetStagedFiles:
    """Tests for get_staged_files function."""

    @patch('honest_anchor.cli.subprocess.run')
    def test_get_staged_files_with_files(self, mock_run, tmp_path):
        """Test getting staged files from git."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="file1.py\nfile2.py\n"
        )

        with CliRunner().isolated_filesystem(temp_dir=tmp_path):
            # Create the files so they pass the exists() check
            Path("file1.py").write_text("print(1)")
            Path("file2.py").write_text("print(2)")

            result = get_staged_files()

            assert result == ["file1.py", "file2.py"]
            mock_run.assert_called_once()

    @patch('honest_anchor.cli.subprocess.run')
    def test_get_staged_files_empty(self, mock_run):
        """Test with no staged files."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )

        result = get_staged_files()

        assert result == []

    @patch('honest_anchor.cli.subprocess.run')
    def test_get_staged_files_git_not_found(self, mock_run):
        """Test when git is not installed."""
        mock_run.side_effect = FileNotFoundError()

        result = get_staged_files()

        assert result == []


class TestCliCommitStaged:
    """Tests for anchor commit --staged command."""

    def test_commit_staged_no_files(self, tmp_path):
        """Test --staged with no staged files."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(cli, ['init'])

            with patch('honest_anchor.cli.get_staged_files', return_value=[]):
                result = runner.invoke(cli, ['commit', '--staged'])

            assert "No staged files" in result.output

    @patch('honest_anchor.cli.run_ots_command')
    @patch('honest_anchor.cli.get_staged_files')
    def test_commit_staged_success(self, mock_staged, mock_ots, tmp_path):
        """Test successful --staged commit."""
        mock_ots.return_value = (True, "Success")
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(cli, ['init'])

            # Create test file
            Path("staged.py").write_text("print('staged')")
            mock_staged.return_value = ["staged.py"]

            # Create fake .ots file
            Path("staged.py.ots").write_bytes(b"fake ots proof")

            result = runner.invoke(cli, ['commit', '--staged'])

            assert "staged" in result.output.lower() or "Anchoring" in result.output

    def test_commit_staged_short_flag(self, tmp_path):
        """Test -s short flag for --staged."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            runner.invoke(cli, ['init'])

            with patch('honest_anchor.cli.get_staged_files', return_value=[]):
                result = runner.invoke(cli, ['commit', '-s'])

            assert "No staged files" in result.output
