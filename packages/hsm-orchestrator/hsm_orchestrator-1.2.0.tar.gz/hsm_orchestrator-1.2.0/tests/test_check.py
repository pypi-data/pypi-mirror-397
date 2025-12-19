import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner
from git import Repo

from hsm_orchestrator import main, exceptions

# from .setup import print_diags
from .setup import set_up_environment, set_up_config, re_search

FIXTURE_DIR = Path(__file__).parent.resolve() / "files"


def test_config_arg_passed_but_no_file(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=False
        )
        config_doesntexist = Path(tmp_path / ".config" / "doesntexist.ini")
        runner.invoke(
            main,
            [
                "check",
                "--config",
                config_doesntexist,
                "--repo-dir",
                repo_dir,
                "--csr-dir",
                csr_dir,
            ],
        )
        assert config_doesntexist.exists()


def test_repo_dir_not_git(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=False
        )
        result = runner.invoke(
            main,
            [
                "check",
                "--config",
                orchestrator_config_file,
                "--repo-dir",
                repo_dir,
                "--csr-dir",
                csr_dir,
            ],
        )
        assert "directory isn't a git working directory" in result.output


def test_repo_dir_wrong_repo(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=False
        )
        Repo.init(repo_dir)
        result = runner.invoke(
            main,
            [
                "check",
                "--config",
                orchestrator_config_file,
                "--repo-dir",
                repo_dir,
                "--csr-dir",
                csr_dir,
            ],
        )
        assert "doesn't have a certs_issued directory within it" in result.output


def test_git_repo_missing_main_branch(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=False
        )
        Path(repo_dir / ".git").mkdir()
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = master\n")
        Repo.init(repo_dir)
        Path(repo_dir / "certs_issued").mkdir()
        result = runner.invoke(
            main,
            [
                "check",
                "--config",
                orchestrator_config_file,
                "--repo-dir",
                repo_dir,
                "--csr-dir",
                csr_dir,
            ],
        )
        re_search(r"The .* git repository is missing a \'main\' branch", result.output)


def test_git_repo_on_main_branch(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=False
        )
        Path(repo_dir / ".git").mkdir()
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
        repo = Repo.init(repo_dir)
        Path(repo_dir / "certs_issued").mkdir()
        repo.index.commit("Adding certs_issued")
        assert repo.active_branch == repo.heads.main


def test_missing_csr_dir(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=False
        )
        Path(repo_dir / ".git").mkdir()
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
        repo = Repo.init(repo_dir)
        Path(repo_dir / "certs_issued").mkdir()
        repo.index.commit("Adding certs_issued")
        result = runner.invoke(
            main,
            [
                "check",
                "--config",
                orchestrator_config_file,
                "--repo-dir",
                repo_dir,
                "--csr-dir",
                csr_dir,
            ],
        )
        re_search(
            r"Error: Invalid value for '--csr-dir': Directory '[^']+' does not exist\.",
            result.output,
        )


def test_missing_csr_file(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=True
        )
        csr_dir.mkdir()
        Path(repo_dir / ".git").mkdir()
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
        repo = Repo.init(repo_dir)
        Path(repo_dir / "certs_issued").mkdir()
        repo.index.commit("Adding certs_issued")
        result = runner.invoke(main, ["check", "--config", orchestrator_config_file])
        re_search(
            r"Error: Invalid value for '--csr-dir': The .* directory doesn't contain a"
            r" \.csr file\.",
            result.output,
        )


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr")
def test_git_repo_missing_remote(tmp_path, datafiles):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=True
        )
        csr_dir.mkdir()
        Path(repo_dir / ".git").mkdir()
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
        repo = Repo.init(repo_dir)
        Path(repo_dir / "certs_issued").mkdir()
        Path(repo_dir / "file.txt").touch()
        repo.index.commit("Adding file.txt")
        csr_file = csr_dir / "example.csr"
        Path(datafiles / "example.csr").rename(csr_file)
        result = runner.invoke(main, ["check", "--config", orchestrator_config_file])
        assert type(result.exception) is type(exceptions.RepoNotReady("foo"))
        re_search(
            r"The .* repo has no remotes configured that match "
            r".* Make sure the repo is setup with an"
            r" 'origin' remote pointing to the GitHub repo\.",
            repr(result.exception),
        )


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr")
def test_git_repo_remotes(tmp_path, datafiles):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=True
        )
        csr_dir.mkdir()
        Path(repo_dir / ".git").mkdir()
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
            f.write('[remote "origin"]\n')
            f.write("url = git@github.com:octocat/someotherrepo.git\n")
            f.write("fetch = +refs/heads/*:refs/remotes/origin/*\n")
        repo = Repo.init(repo_dir)
        Path(repo_dir / "certs_issued").mkdir()
        repo.index.commit("Adding certs_issued")
        csr_file = csr_dir / "example.csr"
        Path(datafiles / "example.csr").rename(csr_file)
        result = runner.invoke(
            main, ["check", "--skip-git-fetch", "--config", orchestrator_config_file]
        )
        assert type(result.exception) is type(exceptions.RepoNotReady("foo"))
        re_search(
            r"The .* repo has no remotes configured that match "
            r".* Make sure the repo is setup with an"
            r" 'origin' remote pointing to the GitHub repo\.",
            repr(result.exception),
        )

        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
            f.write('[remote "origin"]\n')
            f.write("url = git@github.com:mozilla-services/hsm.git\n")
            f.write("fetch = +refs/heads/*:refs/remotes/origin/*\n")
        result = runner.invoke(
            main, ["check", "--skip-git-fetch", "--config", orchestrator_config_file]
        )
        re_search(
            r"The .* repo has no remotes configured that match",
            repr(result.exception),
            reverse=True,
        )
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
            f.write('[remote "origin"]\n')
            f.write("url = https://github.com/mozilla-services/hsm.git\n")
            f.write("fetch = +refs/heads/*:refs/remotes/origin/*\n")
        result = runner.invoke(
            main, ["check", "--skip-git-fetch", "--config", orchestrator_config_file]
        )
        re_search(
            r"The .* repo has no remotes configured that match",
            repr(result.exception),
            reverse=True,
        )
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
            f.write('[remote "origin"]\n')
            f.write("url = https://github.com/mozilla-services/hsm\n")
            f.write("fetch = +refs/heads/*:refs/remotes/origin/*\n")
        result = runner.invoke(
            main, ["check", "--skip-git-fetch", "--config", orchestrator_config_file]
        )
        re_search(
            r"The .* repo has no remotes configured that match",
            repr(result.exception),
            reverse=True,
        )


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "malformed.cnf")
def test_malformed_cnf_file(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "malformed.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                out_file.write(line)

        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="test.crt\n",
        )
        re_search(r"Unable to parse .*example\.cnf", result.output)
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr")
def test_missing_openssl_cnf(tmp_path, datafiles):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=True
        )
        csr_dir.mkdir()
        Path(repo_dir / ".git").mkdir()
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
        repo = Repo.init(repo_dir)
        Path(repo_dir / "certs_issued").mkdir()
        repo.index.commit("Adding certs_issued")
        csr_file = csr_dir / "example.csr"
        Path(datafiles / "example.csr").rename(csr_file)
        repo.create_remote("origin", "git@github.com:mozilla-services/hsm.git")
        Path(repo_dir / "file.txt").touch()
        feature_branch = repo.create_head("feature_branch")
        feature_branch.checkout()

        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", orchestrator_config_file],
            input="",
        )
        re_search(r"The CSR .* has no associated \.cnf file\.", result.output)


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_cnf_csr_match_existing_certs_issued(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(datafiles / "example.cnf").rename(env["cnf_file"])
        Path(env["repo_dir"] / "certs_issued" / "test" / "example.cnf").touch()
        Path(env["repo_dir"] / "certs_issued" / "test" / "example.csr").touch()
        Path(env["repo_dir"] / "certs_issued" / "test" / "example.crt").touch()
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="",
        )
        re_search(
            r"The \.csr file .*, were it to be used to create a \.crt file, would"
            r" create example\.crt which has the same name as the existing issued cert"
            r" .*\. This could cause a collision\. Please change the name of"
            r" .*example\.csr and .*example\.cnf to something distinct\.",
            result.output,
        )


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_default_ca_setting(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if not line.startswith("default_ca"):
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="",
        )
        re_search(
            r"The \.cnf file .* is missing a 'default_ca' value in the 'ca' section"
            r" which is required\.",
            result.output,
        )


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr")
def test_create_branch(tmp_path, datafiles):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=True
        )
        csr_dir.mkdir()
        Path(repo_dir / ".git").mkdir()
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
        repo = Repo.init(repo_dir)
        Path(repo_dir / "certs_issued").mkdir()
        repo.index.commit("Adding certs_issued")
        csr_file = csr_dir / "example.csr"
        Path(datafiles / "example.csr").rename(csr_file)
        repo.create_remote("origin", "git@github.com:mozilla-services/hsm.git")
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", orchestrator_config_file],
            input="create\ntest_branch\n",
        )
        assert "Branch test_branch created and checked out" in result.output


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr")
def test_switch_branch(tmp_path, datafiles):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=True
        )
        csr_dir.mkdir()
        Path(repo_dir / ".git").mkdir()
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
        repo = Repo.init(repo_dir)
        Path(repo_dir / "certs_issued").mkdir()
        repo.index.commit("Adding file.txt")
        csr_file = csr_dir / "example.csr"
        Path(datafiles / "example.csr").rename(csr_file)
        repo.create_remote("origin", "git@github.com:mozilla-services/hsm.git")
        Path(repo_dir / "file.txt").touch()
        repo.create_head("feature_branch")

        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", orchestrator_config_file],
            input="switch\nfeature_branch\n",
        )
        re_search(r"The CSR .* has no associated \.cnf file\.", result.output)


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr")
def test_multiple_csrs(tmp_path, datafiles):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        orchestrator_config_file, repo_dir, csr_dir = set_up_config(
            tmp_path, configure_paths=True
        )
        csr_dir.mkdir()
        Path(repo_dir / ".git").mkdir()
        with Path(repo_dir / ".git" / "config").open("w") as f:
            f.write("[init]\n   defaultBranch = main\n")
        repo = Repo.init(repo_dir)
        Path(repo_dir / "certs_issued").mkdir()
        repo.index.commit("Adding file.txt")
        csr_file = csr_dir / "example.csr"
        Path(datafiles / "example.csr").rename(csr_file)
        shutil.copy2(csr_file, Path(csr_dir / "example2.csr"))
        repo.create_remote("origin", "git@github.com:mozilla-services/hsm.git")
        Path(repo_dir / "file.txt").touch()
        repo.create_head("feature_branch")

        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", orchestrator_config_file],
            input="switch\nfeature_branch\nexample.csr\n",
        )
        re_search(r"Which CSR would you like to use\?", result.output)
        re_search(r"The CSR .* has no associated \.cnf file\.", result.output)
        assert result.exit_code != 0


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr")
def test_empty_openssl_cnf(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        env["cnf_file"].touch()
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="",
        )
        re_search(
            r"The \.cnf file .* is missing a 'ca' section which is required\.",
            result.output,
        )


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_default_startdate(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if not line.startswith("default_startdate"):
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="y\n",
        )
        assert "There is no start date configured" in result.output


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_default_enddate(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if not line.startswith("default_enddate"):
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="y\n",
        )
        assert "There is no end date configured" in result.output
        with env["cnf_file"].open("r") as f:
            assert any(x.startswith("default_enddate") for x in f)


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_private_key_setting(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if not line.startswith("private_key"):
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="simple_example\n",
        )
        re_search(r"You must set the 'private_key' value in the .* file", result.output)


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_wrong_private_key_value(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if line.startswith("private_key"):
                    out_file.write(
                        "private_key	= simple_doesnotexist   # The private key\n"
                    )
                else:
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="simple_example\n",
        )
        re_search(
            r"What would you like to change the 'private_key' value in the"
            r" .*example.cnf to\? \[",
            result.output,
        )


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_using_test_private_key(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        repo_dir = env["repo_dir"]
        Path(repo_dir / "certificate-authorities" / "simple_test").mkdir()
        Path(repo_dir / "certificate-authorities" / "simple_test" / "test").mkdir()
        Path(
            repo_dir / "certificate-authorities" / "simple_test" / "test" / "test.crt"
        ).touch()
        with Path(
            repo_dir / "certificate-authorities" / "simple_test" / "test" / "serial"
        ).open("w") as f:
            f.write("01")
        with Path(
            repo_dir / "certificate-authorities" / "simple_test" / "test" / "index.txt"
        ).open("w") as f:
            f.write(
                "V\t22511013200827Z\t\t01\tunknown\t/C=US/O=Mozilla"
                " Corporation/OU=Mozilla AMO Production Signing Service/CN=test"
            )
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if line.startswith("private_key"):
                    out_file.write("private_key	= simple_test   # The private key\n")
                else:
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="n\n",
        )
        re_search(
            r"The 'private_key' in the .* file is set to 'simple_test' which is a test"
            r" private key\. Would you like to change it to something different\?",
            result.output,
        )
        re_search(
            r"What would you like to change the 'private_key' value in the"
            r" .*example.cnf to\? \[",
            result.output,
            reverse=True,
        )
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="y\nsimple_example\n",
        )
        re_search(
            r"The 'private_key' in the .* file is set to 'simple_test' which is a test"
            r" private key\. Would you like to change it to something different\?",
            result.output,
        )
        re_search(
            r"What would you like to change the 'private_key' value in the"
            r" .*example.cnf to\? \[",
            result.output,
        )


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_certificate_setting(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if not line.startswith("certificate"):
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="test.crt\n",
        )
        re_search(r"The 'certificate' value in the .* file is missing\.", result.output)


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_wrong_certificate_value(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if line.startswith("certificate"):
                    out_file.write(
                        "certificate	= $dir/doesnotexist.crt 	# The CA certificate\n"
                    )
                else:
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="test.crt\n",
        )
        re_search(
            r"What would you like to change the 'certificate' value in the .* to\?",
            result.output,
        )


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_unique_subject_yes(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if line.startswith("unique_subject"):
                    out_file.write(
                        "unique_subject	= yes			# Mozilla CA has issued multiple certs with"
                        " the same subject\n"
                    )
                else:
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="y\n",
        )
        re_search(
            r'The "unique_subject" field in .* is set to yes \(the default\).',
            result.output,
        )
        with env["cnf_file"].open("r") as f:
            assert any(line.startswith("unique_subject = no") for line in f)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if not line.startswith("unique_subject"):
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="y\n",
        )
        re_search(
            r'The "unique_subject" field in .* is set to yes \(the default\).',
            result.output,
        )


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_serial_file(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if line.startswith("serial"):
                    out_file.write(
                        "serial		= $dir/serial_doesnotexist 		# The current serial number\n"
                    )
                else:
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="test.crt\n",
        )
        re_search(
            r"The file .* is missing\. This would be the case if the .* is incorrect,"
            r" the serial value in .* was wrong or if this is a newly created"
            r" certificate authority\.",
            result.output,
        )
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_serial_setting(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if not line.startswith("serial"):
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="y\n",
        )
        re_search(
            r'There is no "serial" value configured in the .*example\.cnf'
            r" file.\nWould you like to have the cnf file updated to set serial to"
            r' "serial"\? \[y/n]: ',
            result.output,
        )
        with env["cnf_file"].open("r") as f:
            assert any(x == "serial = serial\n" for x in f)
        assert result.exit_code == 0


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_missing_database(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        with (
            Path(datafiles / "example.cnf").open("r") as in_file,
            env["cnf_file"].open("w") as out_file,
        ):
            for line in in_file:
                if line.startswith("database"):
                    out_file.write(
                        "database	= $dir/index_doesnotexist.txt	# database index file.\n"
                    )
                else:
                    out_file.write(line)
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="test.crt\n",
        )
        re_search(
            r"The file .* is missing\. This would be the case if the .* is incorrect,"
            r" the database value in .* was wrong or if this is a newly created"
            r" certificate authority\.",
            result.output,
        )
        assert result.exit_code == 1


@pytest.mark.datafiles(FIXTURE_DIR / "example.csr", FIXTURE_DIR / "example.cnf")
def test_check(tmp_path, datafiles, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_path):
        env = set_up_environment(tmp_path, datafiles, monkeypatch)
        Path(datafiles / "example.cnf").rename(env["cnf_file"])
        result = runner.invoke(
            main,
            ["check", "--skip-git-fetch", "--config", env["orchestrator_config_file"]],
            input="",
        )
        re_search(
            r"Check completed\.",
            result.output,
        )
        assert result.exit_code == 0
