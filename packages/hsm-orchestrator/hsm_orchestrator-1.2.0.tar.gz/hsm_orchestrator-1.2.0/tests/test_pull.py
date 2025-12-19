import stat
from pathlib import Path

import pytest
from click.testing import CliRunner
from rich.text import Text

from hsm_orchestrator import main
from .setup import set_up_environment, re_search, set_up_usb

# from .setup import print_diags

FIXTURE_DIR = Path(__file__).parent.resolve() / "files"


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_empty_usb_stick(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert "Which mount is the USB stick you would you like to use" in result.output
        assert (
            "No .crt files were found on the USB stick with names that match CA"
            " certificate files"
            in result.output
        )
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_multiple_ca_crt_files(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(env["usb_mount_point"] / "test.crt").touch()
        Path(env["usb_mount_point"] / "foo.crt").touch()
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert (
            "There are multiple .crt files on the USB stick with names that match CA"
            " certificate files"
            in result.output
        )
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_no_crt_files(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(env["usb_mount_point"] / "test.crt").touch()
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert (
            "There aren't any .crt files (other than the CA .crt file) on the USB"
            " stick."
            in Text.from_ansi(result.output).plain
        )
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_crt_related_files(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(env["usb_mount_point"] / "test.crt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.crt").touch()
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert (
            "The AUT-123-testing.crt file is missing some of the expected associated"
            " files"
            in Text.from_ansi(result.output).plain
        )
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_ca_related_files(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(env["usb_mount_point"] / "test.crt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.crt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.cnf").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.csr").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.output.txt").touch()
        Path(env["usb_mount_point"] / "AUT-123-testing.instructions.txt").touch()
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert "Some of the expected CA files are missing" in result.output
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_file_actions_table_output(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        set_up_usb(env["usb_mount_point"])
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        result_lines = result.output.splitlines()
        re_search(r"^delete *: usb[/\\]test\.crt$", result_lines)
        re_search(r"^delete *: usb[/\\]unrelated-file\.txt$", result_lines)
        re_search(
            r"repo[/\\]certs_issued[/\\]test *: usb[/\\]AUT-123-testing\.crt$",
            result_lines,
        )
        re_search(
            r"repo[/\\]certs_issued[/\\]test *: usb[/\\]AUT-123-testing\.csr$",
            result_lines,
        )
        re_search(
            r"repo[/\\]certs_issued[/\\]test *: usb[/\\]AUT-123-testing\.cnf$",
            result_lines,
        )
        re_search(
            r"repo[/\\]certs_issued[/\\]test *:"
            r" usb[/\\]AUT-123-testing\.output\.txt$",
            result_lines,
        )
        re_search(
            r"repo[/\\]certs_issued[/\\]test *:"
            r" usb[/\\]AUT-123-testing\.instructions\.txt$",
            result_lines,
        )
        re_search(
            r"repo[/\\]certificate-authorities[/\\]simple_example[/\\]test *:"
            r" usb[/\\]serial$",
            result_lines,
        )
        re_search(
            r"repo[/\\]certificate-authorities[/\\]simple_example[/\\]test *:"
            r" usb[/\\]index\.txt$",
            result_lines,
        )
        re_search(r"^ignore *: usb[/\\]unrelated-directory$", result_lines)


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_file_actions(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        set_up_usb(env["usb_mount_point"])
        # Remove the certs_issued directory to make sure it gets created
        Path(env["repo_dir"] / "certs_issued" / "test").rmdir()
        # Set the execute bits on the file so that we can test that they are
        # cleared during the pull
        Path(env["usb_mount_point"] / "AUT-123-testing.crt").chmod(0o755)
        keyboard_input = f"{env['usb_mount_point']}\nn\ny\n"
        result = runner.invoke(
            main,
            [
                "pull-from-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert not Path(env["usb_mount_point"] / "test.crt").exists()
        assert not Path(env["usb_mount_point"] / "unrelated-file.txt").exists()
        assert not Path(env["usb_mount_point"] / "serial").exists()
        assert not Path(env["usb_mount_point"] / "index.txt").exists()
        assert not Path(env["usb_mount_point"] / "AUT-123-testing.crt").exists()
        assert not Path(env["usb_mount_point"] / "AUT-123-testing.cnf").exists()
        assert not Path(env["usb_mount_point"] / "AUT-123-testing.csr").exists()
        assert not Path(env["usb_mount_point"] / "AUT-123-testing.output.txt").exists()
        assert not Path(
            env["usb_mount_point"] / "AUT-123-testing.instructions.txt"
        ).exists()

        assert Path(env["usb_mount_point"] / "unrelated-directory").exists()
        ca_path = (
            env["repo_dir"] / "certificate-authorities" / "simple_example" / "test"
        )
        assert Path(ca_path / "serial").exists()
        assert Path(ca_path / "index.txt").exists()
        cert_path = env["repo_dir"] / "certs_issued" / "test"
        assert (
            cert_path.exists()
        ), "The certs_issued/test directory should have been created"
        assert Path(cert_path / "AUT-123-testing.crt").exists()
        mode = Path(cert_path / "AUT-123-testing.crt").stat().st_mode
        assert not (
            mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        ), "The execute bits on the file should have been cleared"
        assert Path(cert_path / "AUT-123-testing.cnf").exists()
        assert Path(cert_path / "AUT-123-testing.csr").exists()
        assert Path(cert_path / "AUT-123-testing.output.txt").exists()
        assert Path(cert_path / "AUT-123-testing.instructions.txt").exists()
        assert result.exit_code == 0
