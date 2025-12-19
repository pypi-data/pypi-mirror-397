import re
from pathlib import Path
from typing import Any

import click
import git
import git.exc

from hsm_orchestrator import exceptions


def validate_repo_dir(ctx: click.Context, param: click.Parameter, value: Any) -> Path:
    """Validate the git repository

    :param ctx: The Click context.
    :type ctx: click.Context
    :param param: The Click parameter.
    :type param: click.Parameter
    :param value: Path to the git repo
    :type value: Any
    :returns: Path:

    """
    repo_dir = value
    try:
        repo = git.Repo(repo_dir)
    except git.exc.InvalidGitRepositoryError:
        raise click.BadParameter(
            f"The {repo_dir} directory isn't a git working directory."
        )
    if not Path(repo_dir / Path("certs_issued")).exists():
        raise click.BadParameter(
            f"The {repo_dir} directory doesn't have a certs_issued directory within it."
            " Is this the right directory?"
        )
    if "main" not in repo.heads:
        raise click.BadParameter(
            f"The {repo_dir} git repository is missing a 'main' branch"
        )

    return Path(repo_dir)


def validate_csr_dir(ctx: click.Context, param: click.Parameter, value: Any) -> Path:
    """Validate the CSR directory, confirming it contains a CSR

    :param ctx: The Click context.
    :type ctx: click.Context
    :param param: The Click parameter.
    :type param: click.Parameter
    :param value: Path to the CSR directory
    :type value: Any
    :returns: Path:

    """
    csr_dir = Path(value)
    csr_files = [x for x in csr_dir.glob("*.csr")]
    if not csr_files:
        raise click.BadParameter(
            f"The {csr_dir} directory doesn't contain a .csr file."
        )
    return csr_dir


def validate_environment(
    repo: git.repo.base.Repo, remote_url_pattern: re.Pattern
) -> str:
    """Validate the environment

    Look that there's an expected git remote and that we're not running on the
    offline HSM

    :param repo: git.repo.base.Repo: A GitPython repo object for the git repo
    :param remote_url_suffix: str: The string we expect at the end of the remote
           URL for the git repo
    :returns: str: The git remote name

    """
    if Path("/opt/nfast/kmdata/local").exists():
        # Note to test this we may need something like
        # https://github.com/pytest-dev/pyfakefs to mock an absolute file location
        raise exceptions.WrongSystem(
            "Found /opt/nfast/kmdata/local which implies hsm-orchestrator is being run"
            " on the offline HSM server. hsm-orchestrator should only be run on your"
            " local workstation."
        )

    # Check git remote
    remote_name = None
    for remote in repo.remotes:
        if remote_url_pattern.search(remote.url) is not None:
            remote_name = remote.name
    if remote_name is None:
        raise exceptions.RepoNotReady(
            f"The {repo.working_tree_dir} repo has no remotes configured that match "
            f"'{remote_url_pattern}'. Make sure the repo is setup with an 'origin' "
            "remote pointing to the GitHub repo."
        )

    return remote_name
