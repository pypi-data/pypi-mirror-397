from pathlib import Path

import pytest
from click.testing import CliRunner
import psutil
from typing import Any

from hsm_orchestrator import main
from .setup import set_up_environment, re_search

# from .setup import print_diags

FIXTURE_DIR = Path(__file__).parent.resolve() / "files"


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_selecting_usb_stick(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(datafiles / "example.cnf").rename(env["cnf_file"])
        keyboard_input = f"{env['usb_mount_point']}\n"
        result = runner.invoke(
            main,
            [
                "push-to-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert "Which mount is the USB stick you would you like to use" in result.output
        assert "Would you like to save this path" in result.output


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_selecting_usb_stick_with_unsupported_filesystem(
    tmp_path, datafiles, monkeypatch
):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, create_usb_stick=False)

        # Mock up a fake USB flash drive
        bad_usb_mount_point = tmp_path / "usb_bad_fs"
        bad_usb_mount_point.mkdir()
        usb_mount_point = tmp_path / "usb"
        usb_mount_point.mkdir()
        fake_partitions = [
            psutil._common.sdiskpart(
                device="/dev/sda1", mountpoint="/", fstype="ext4", opts="rw"
            ),
            psutil._common.sdiskpart(
                device="/dev/sdb1",
                mountpoint=str(usb_mount_point),
                fstype="exfat",
                opts="rw",
            ),
            psutil._common.sdiskpart(
                device="/dev/sdc1",
                mountpoint=str(bad_usb_mount_point),
                fstype="fuseblk",  # fuseblk is what the ntfs-3g FUSE filesystem shows up as
                opts="rw",
            ),
        ]

        def fake_disk_partitions(all: bool = False) -> Any:
            return fake_partitions

        if monkeypatch is not None:
            monkeypatch.setattr(psutil, "disk_partitions", fake_disk_partitions)

        Path(datafiles / "example.cnf").rename(env["cnf_file"])

        # Enter a mount with an unsupported filesystem and fail
        keyboard_input = f"{bad_usb_mount_point}\n"
        result = runner.invoke(
            main,
            [
                "push-to-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert "Which mount is the USB stick you would you like to use" in result.output
        re_search(
            r"The .* device uses the .* filesystem which isn't supported by the offline"
            r" HSM OS\. Choose a different device\.",
            result.output,
        )
        assert "Would you like to save this path" not in result.output

        # First enter a mount with an unsupported filesystem,
        # then enter a mount with a supported filesystem
        keyboard_input = f"{bad_usb_mount_point}\n{usb_mount_point}\n"
        result = runner.invoke(
            main,
            [
                "push-to-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert "Which mount is the USB stick you would you like to use" in result.output
        re_search(
            r"The .* device uses the .* filesystem which isn't supported by the offline"
            r" HSM OS\. Choose a different device\.",
            result.output,
        )
        assert "Would you like to save this path" in result.output


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_save_usb_stick_to_config(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(datafiles / "example.cnf").rename(env["cnf_file"])
        keyboard_input = f"{env['usb_mount_point']}\ny\n"
        runner.invoke(
            main,
            [
                "push-to-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        with env["orchestrator_config_file"].open("r") as f:
            assert f"usb_stick_path = {env['usb_mount_point']}" in f.read()


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_read_usb_stick_mount_from_config(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(datafiles / "example.cnf").rename(env["cnf_file"])
        with env["orchestrator_config_file"].open("a") as f:
            f.write(f"usb_stick_path = {env['usb_mount_point']}\n")
        keyboard_input = "y\n"
        result = runner.invoke(
            main,
            [
                "push-to-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        re_search(
            r"The instructions and files have been written to .*usb USB stick\.",
            result.output,
        )
        assert result.exit_code == 0


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_push(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(datafiles / "example.cnf").rename(env["cnf_file"])
        keyboard_input = f"{env['usb_mount_point']}\nn\n"
        result = runner.invoke(
            main,
            [
                "push-to-stick",
                "--skip-git-fetch",
                "--config",
                env["orchestrator_config_file"],
            ],
            input=keyboard_input,
        )
        assert "The instructions and files have been written to" in result.output
        assert result.exit_code == 0


# TODO : Add check that all files were copied
