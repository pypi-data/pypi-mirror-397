import datetime
import stat
import re
import shutil
from pathlib import Path, PurePath
from typing import Any

import click
import git
import git.exc
import psutil
import rich.theme
from configobj import ConfigObj, ConfigObjError
from platformdirs import user_config_path
from rich import print
from rich.prompt import Confirm

from hsm_orchestrator import validators
from hsm_orchestrator.overrides import Prompt

# This will have a value like
# 'C:\Users\jdoe\AppData\Local\Mozilla\hsm-orchestrator\config.ini'
# or '/Users/jdoe/Library/Application Support/hsm-orchestrator/config.ini'
# or '/home/jdoe/.config/hsm-orchestrator/config.ini'
DEFAULT_CONFIG_FILE = user_config_path(
    appname="hsm-orchestrator", appauthor="Mozilla"
) / Path("config.ini")
DEFAULT_CERT_DURATION = datetime.timedelta(days=365 * 5)
DEFAULT_CERT_START_DAYS_AGO = datetime.timedelta(days=30)
SUPPORTED_FILESYSTEMS = [
    "ext4",
    "ext3",
    "ext2",
    "iso9660",
    "vfat",
    "exfat",
    "hfs",
    "hfsplus",
]

rich.reconfigure(
    theme=rich.theme.Theme({"q": "bold green", "e": "bold purple"}), soft_wrap=True
)


class HsmOrchestrator:
    def __init__(self, orchestrator_config_filename: Path, **kwargs: Any) -> None:
        """Initialize the HsmOrchestrator.

        :param orchestrator_config_filename: Path to the orchestrator configuration
               file.
        :type orchestrator_config_filename: Path
        :returns: None

        """
        self.orchestrator_config_filename = orchestrator_config_filename
        self.remote_url_pattern = re.compile(r".*mozilla-services/hsm(\.git)?")
        self.repo_dir = kwargs["repo_dir"] if "repo_dir" in kwargs else None
        self.csr_dir = kwargs["csr_dir"] if "csr_dir" in kwargs else None

        # The orchestrator_config only contains values in the config.ini file, not
        # arguments passed on the command line
        self.orchestrator_config = ConfigObj(str(self.orchestrator_config_filename))
        self.csr_file = None
        self.cnf_file = None
        self.ca_cert_file = None
        self.openssl_config = None
        self.usb_path = None
        # The path on the workstation to the certificate authorities directory
        self.local_ca_path = None
        self.ca_cert_files_in_repo = []

    def get_openssl_cnf_config(self) -> None:
        """Parse the OpenSSL configuration (.cnf) file.

        Loads the OpenSSL configuration into a ConfigObj instance, cleans up inline
        comments, and stores it in `self.openssl_config`.

        OpenSSL Config format : https://docs.openssl.org/master/man5/config/

        :raises ConfigObjError: If the configuration file cannot be parsed.
        :returns: None

        """
        try:
            self.openssl_config = ConfigObj(
                infile=str(self.cnf_file),
                # We can't pass the Path object directly because of
                # https://github.com/DiffSK/configobj/issues/235
                list_values=False,  # OpenSSL config doesn't support lists
                interpolation="Template",  # string.Template style interpolation which
                # is close to OpenSSL syntax
            )
        except ConfigObjError:
            print(
                f"Unable to parse {self.cnf_file}.\nSometimes this is caused by"
                " duplicate keys in a section. OpenSSL allows keys to be set multiple"
                " times and just uses the last one set, but this can be confusing and"
                " we should avoid duplicated keys."
            )
            raise
        # Note : Using the configobj Python package sacrifices
        # * whitespace between key and equal sign and between equal sign and value
        # * all but 1 whitespace between the end of a value and an inline comment
        # * whitespace around section names within brackets

        # While waiting for this PR ( https://github.com/DiffSK/configobj/pull/262 ) to
        # be released this is a workaround to the missing space between the value and
        # the inline comment
        pattern = re.compile(r"^#\s*")
        for section in self.openssl_config.sections:
            for key, inline_comment in self.openssl_config[
                section
            ].inline_comments.items():
                if inline_comment is not None:
                    self.openssl_config[section].inline_comments[key] = pattern.sub(
                        "", inline_comment
                    )

    def get_ca_cert_filename_on_usb(self) -> str:
        """Identify which file on USB stick is the CA cert

        Compare files on the USB stick with CA certificate files in the repo
        to identify which one is the CA certificate

        :returns: The filename of the CA certificate on the USB stick
        """
        for private_key_directory in [
            x
            for x in Path(self.repo_dir / "certificate-authorities").iterdir()
            if x.is_dir()
        ]:
            for certificate_authority_directory in private_key_directory.iterdir():
                for certificate_file in certificate_authority_directory.iterdir():
                    self.ca_cert_files_in_repo.append(certificate_file)
        crt_filenames_on_usb = set(x.name for x in self.usb_path.glob("*.crt"))
        ca_cert_filenames_on_usb = (
            set(x.name for x in self.ca_cert_files_in_repo) & crt_filenames_on_usb
        )
        if len(ca_cert_filenames_on_usb) == 0:
            print(
                "No .crt files were found on the USB stick with names that match CA"
                " certificate files.We would expect there to be one CA certificate file"
                " on the USB stick."
            )
            exit(1)
        if len(ca_cert_filenames_on_usb) > 1:
            print(
                "There are multiple .crt files on the USB stick with names that match"
                " CA certificate files.We would only expect there to be one CA"
                " certificate file on the USB stick."
            )
            exit(1)
        ca_cert_filename_on_usb = next(iter(ca_cert_filenames_on_usb))
        return ca_cert_filename_on_usb

    def check_update_private_key(self) -> None:
        """Validate and update the OpenSSL 'private_key' value.

        Prompts the user if the referenced files are missing or invalid and writes
        updates back to the OpenSSL configuration file.

        :returns: None

        """
        # 'private_key' OpenSSL config value is the offline HSM application key to use
        # for signing, equivalent to the -keyfile CLI argument
        private_key_name = self.openssl_config[
            self.openssl_config["ca"]["default_ca"]
        ].get("private_key")

        ca_dir = Path(self.repo_dir / Path("certificate-authorities"))
        possible_private_key_names = [x.name for x in ca_dir.iterdir() if x.is_dir()]
        prompt_for_private_key = False
        if not private_key_name:
            prompt_for_private_key = True
            print(
                f"You must set the 'private_key' value in the {self.cnf_file} file."
                " It's currently not set."
            )
        elif not Path(ca_dir / Path(private_key_name)).exists():
            prompt_for_private_key = True
            print(
                f"The 'private_key' value in the {self.cnf_file} file of"
                f" '{private_key_name}' doesn't map to a directory in the"
                " hsm/certificate-authorities/ directory."
            )
        elif private_key_name == "simple_test":
            prompt_for_private_key = Confirm.ask(
                f"The 'private_key' in the {self.cnf_file} file is set to 'simple_test'"
                " which is a test private key. [q]Would you like to change it to"
                " something different?[/q]"
            )
        if prompt_for_private_key:
            private_key_name = Prompt.ask(
                "[q]What would you like to change the 'private_key' value in the"
                f" {self.cnf_file} to?[/q]",
                choices=possible_private_key_names,
            )
            self.openssl_config[self.openssl_config["ca"]["default_ca"]][
                "private_key"
            ] = private_key_name
            self.openssl_config.write()

    def check_update_ca_crt(self) -> None:
        """Validate and update the OpenSSL 'certificate' value.

        Prompts the user if the referenced files are missing or invalid and writes
        updates back to the OpenSSL configuration file.

        :returns: None

        """
        ca_crt_name = self.openssl_config[self.openssl_config["ca"]["default_ca"]].get(
            "certificate"
        )
        ca_dir = Path(self.repo_dir / Path("certificate-authorities"))
        private_key_name = self.openssl_config[
            self.openssl_config["ca"]["default_ca"]
        ].get("private_key")
        private_key_path = Path(ca_dir / Path(private_key_name))

        prompt_for_certificate = False
        if not ca_crt_name:
            prompt_for_certificate = True
            print(f"The 'certificate' value in the {self.cnf_file} file is missing.")

        self.local_ca_path = private_key_path / Path(
            Path(ca_crt_name).with_suffix("").name
        )
        if not self.local_ca_path.exists():
            prompt_for_certificate = True
            print(
                f"The 'certificate' value in the {self.cnf_file} file of"
                f" '{ca_crt_name}' implies a directory of {self.local_ca_path} but it"
                " doesn't exist."
            )
        if not Path(self.local_ca_path / Path(ca_crt_name).name).exists():
            prompt_for_certificate = True
            print(
                f"The 'certificate' value in the {self.cnf_file} file of"
                f" '{ca_crt_name}' doesn't map to a CA certificate file located at"
                f" {Path(self.local_ca_path / Path(ca_crt_name).name)}"
            )
        if prompt_for_certificate:
            possible_ca_crt_names = []
            for ca in private_key_path.iterdir():
                if Path(ca / Path(ca.name).with_suffix(".crt")).exists():
                    possible_ca_crt_names.append(Path(ca.name).with_suffix(".crt").name)
            ca_crt_name = Prompt.ask(
                "[q]What would you like to change the 'certificate' value in the"
                f" {self.cnf_file} to?[/q]",
                choices=possible_ca_crt_names,
            )
            self.local_ca_path = private_key_path / Path(Path(ca_crt_name).name)
            self.openssl_config[self.openssl_config["ca"]["default_ca"]][
                "certificate"
            ] = ca_crt_name
            self.openssl_config.write()
        self.ca_cert_file = Path(self.local_ca_path / ca_crt_name)

    def check_update_start_end_date(self) -> None:
        """Ensure that certificate start and end dates are set in the OpenSSL config.

        Prompts the user to add default values if missing.

        :returns: None

        """
        # https://docs.openssl.org/3.1/man1/openssl-ca/#options
        # The format of the start and end date is YYMMDDHHMMSSZ (the same as an ASN1
        # UTCTime structure), or YYYYMMDDHHMMSSZ (the same as an ASN1 GeneralizedTime
        # structure)
        # We're creating the strings by hand instead of using the pyasn1 package and
        # pyasn1.type.useful.GeneralizedTime for simplicity
        if (
            "default_startdate"
            not in self.openssl_config[self.openssl_config["ca"]["default_ca"]]
        ):
            start_datetime = (
                datetime.datetime.now(datetime.timezone.utc)
                - DEFAULT_CERT_START_DAYS_AGO
            )
            start_date = start_datetime.strftime("%Y%m%d%H%M%SZ")
            if Confirm.ask(
                "There is no start date configured.\n[q]Would you like to have the cnf"
                " file updated to set it to the Mozilla default of"
                f" {DEFAULT_CERT_START_DAYS_AGO.days} days ago ({start_date})?[/q]"
            ):
                self.openssl_config[self.openssl_config["ca"]["default_ca"]][
                    "default_startdate"
                ] = start_date
                self.openssl_config.write()
        if (
            "default_enddate"
            not in self.openssl_config[self.openssl_config["ca"]["default_ca"]]
        ):
            end_datetime = (
                datetime.datetime.now(datetime.timezone.utc) + DEFAULT_CERT_DURATION
            )
            end_date = end_datetime.strftime("%Y%m%d%H%M%SZ")
            if Confirm.ask(
                "There is no end date configured\n[q]Would you like to have the cnf"
                " file updated to set it to the Mozilla default of"
                f" {DEFAULT_CERT_DURATION.days / 365:.0f} years from now"
                f" ({end_date})?[/q]"
            ):
                self.openssl_config[self.openssl_config["ca"]["default_ca"]][
                    "default_enddate"
                ] = end_date
            self.openssl_config.write()

    def check_update_unique_subject(self) -> None:
        if (
            "unique_subject"
            not in self.openssl_config[self.openssl_config["ca"]["default_ca"]]
            or self.openssl_config[self.openssl_config["ca"]["default_ca"]][
                "unique_subject"
            ].lower()
            == "yes"
        ):
            if Confirm.ask(
                f'The "unique_subject" field in {self.cnf_file} is set to yes (the'
                " default). The existing Mozilla CA has issued certificates with"
                ' non-unique subjects and "no" is recommended. [q]Would you like it to'
                ' be changed to "no"?[/q]'
            ):
                self.openssl_config[self.openssl_config["ca"]["default_ca"]][
                    "unique_subject"
                ] = "no"
                self.openssl_config.write()

    def check_ca_files(self) -> None:
        """Verify that required CA files exist (serial, index.txt).

        Prompts the user to update the config if values are missing.

        :returns: None

        """
        ca_files = {"serial": Path("serial"), "database": Path("index.txt")}
        # Note : We don't care about index.txt.old serial.old index.txt.attr and
        # index.txt.attr.old index.txt.attr and index.txt.attr.old are just the
        # unique_subject value from the cnf file and will be recreated when openssl-ca
        # is next run
        for key, filename in ca_files.items():
            if key not in [
                str(x)
                for x in self.openssl_config[self.openssl_config["ca"]["default_ca"]]
            ]:
                if Confirm.ask(
                    f'There is no "{key}" value configured in the'
                    f" {self.cnf_file} file.\n[q]Would you like to have the cnf file"
                    f' updated to set {key} to "{filename}"?[/q]'
                ):
                    self.openssl_config[self.openssl_config["ca"]["default_ca"]][
                        key
                    ] = str(filename)
                    self.openssl_config.write()
            value = self.openssl_config[self.openssl_config["ca"]["default_ca"]][key]
            if not Path(self.local_ca_path / value).exists():
                print(
                    f"The file {Path(self.local_ca_path / value)} is missing. This"
                    f" would be the case if the {self.local_ca_path} is incorrect, the"
                    f" {key} value in {self.cnf_file} was wrong or if this is a newly"
                    " created certificate authority."
                )
                exit(1)

    def check_for_matching_issued_cert(self):
        """Check to see if there is an existing cert which matches the .cnf/.csr

        To prevent issuing a duplicate cert with the same name as an existing
        issued cert, compare the .cnf/.csr filenames with the existing certs
        in the certs_issued directory.
        """
        issued_cert_map = {
            x.name: x for x in Path(self.repo_dir / "certs_issued").glob("**/*.crt")
        }
        if self.csr_file.with_suffix(".crt").name in issued_cert_map.keys():
            print(
                f"The .csr file {self.csr_file}, were it to be used to create a .crt"
                f" file, would create {self.csr_file.with_suffix('.crt').name} which"
                " has the same name as the existing issued cert"
                f" {issued_cert_map[self.csr_file.with_suffix('.crt').name]}. This"
                f" could cause a collision. Please change the name of {self.csr_file}"
                f" and {self.cnf_file} to something distinct."
            )
            exit(1)

    def check_update_cnf_file(self) -> None:
        """Perform validation and update of the OpenSSL .cnf file.

        :raises click.BadParameter: If required sections or values are missing.
        :returns: None

        """
        if not self.cnf_file.exists():
            raise click.BadParameter(
                f"The CSR {self.csr_file} has no associated .cnf file."
            )
        if "ca" not in self.openssl_config:
            raise click.BadParameter(
                f"The .cnf file {self.cnf_file} is missing a 'ca' section which is"
                " required."
            )
        if "default_ca" not in self.openssl_config["ca"]:
            raise click.BadParameter(
                f"The .cnf file {self.cnf_file} is missing a 'default_ca' value in the"
                " 'ca' section which is required."
            )
        self.check_update_start_end_date()
        self.check_update_private_key()
        self.check_update_ca_crt()
        self.check_update_unique_subject()
        self.check_ca_files()

    def check_environment(self, skip_git_fetch: bool) -> None:
        """Validate the git environment and prepare for CSR processing.

        :param skip_git_fetch: Whether to skip fetching from the remote repository.
        :type skip_git_fetch: bool
        :returns: None

        """
        repo = git.Repo(self.repo_dir)
        git_remote_name = validators.validate_environment(repo, self.remote_url_pattern)

        if not skip_git_fetch:
            # Git fetch
            print(
                f"Fetching {git_remote_name} from {repo.remotes[git_remote_name].url}"
            )
            # TODO : Add a progressbar to the fetch
            repo.remotes[git_remote_name].fetch()

        branch_state = self.create_or_switch_to_branch(repo)
        if branch_state == "created":
            print(
                "You can now add the .csr and .cnf files to the CSR directory. Once"
                " complete, re-run the hsm-orchestrator"
            )
            exit(0)

        self.csr_file = self.choose_csr()
        # TODO : Add check that the CSR filename has a ticket number in it
        self.cnf_file = self.csr_file.with_suffix(".cnf") if self.csr_file else None

    def create_or_switch_to_branch(self, repo: git.repo.base.Repo) -> str:
        """Create a new git branch or switch to an existing one.

        :param repo: The git repository object.
        :type repo: git.repo.base.Repo
        :returns: 'created' if a new branch was created, 'switched' otherwise.
        :rtype: str

        """
        # Check active branch
        if repo.active_branch in [
            x for x in repo.heads if x.name in ["main", "master"]
        ]:
            branches = [x.name for x in repo.heads]
            branch_list = "\n".join(branches)
            create_branch_or_switch = Prompt.ask(
                f"The local git repo is currently on the '{repo.active_branch}'"
                f" branch.\n\nBranches are :\n{branch_list}\n\n[q]Would you like to"
                " create a new branch in which to put the CSR and other files or"
                " switch to an existing branch?[/q]",
                choices=["create", "switch"],
            )
            if (
                create_branch_or_switch == "create"
            ):  # TODO : test if this will this work with uppercase word create
                branch_name = Prompt.ask(
                    "[q]What branch name would you like to use for the new branch?[/q]"
                    " It should be in the form of"
                    " [e]AUT-123-May2025-new-intermediate[/e]."
                )
                branch = repo.create_head(branch_name)
                branch.checkout()
                print(f"Branch {branch} created and checked out.")
                return "created"
            elif create_branch_or_switch == "switch":
                branch_name = Prompt.ask(
                    "[q]Which branch would you like to switch to?[/q]",
                    choices=[x.name for x in repo.heads],
                )
                repo.heads[str(branch_name)].checkout()
                return "switched"
        return f"already on {repo.active_branch}"

    def choose_usb_disk(self) -> None:
        """Prompt the user to select a USB stick for use.

        :returns: None

        """
        if "usb_stick_path" in self.orchestrator_config and self.orchestrator_config[
            "usb_stick_path"
        ] in [x.mountpoint for x in psutil.disk_partitions()]:
            if Confirm.ask(
                "[q]Would you like to use this USB stick?[/q] :"
                f" {self.orchestrator_config['usb_stick_path']}"
            ):
                self.usb_path = Path(self.orchestrator_config["usb_stick_path"])
        while self.usb_path in [None, "rescan"]:

            # TODO : Look for exfat filesystems which won't work on Oracle Linux

            # This filters out snap mounts on Linux and the root mount
            mounts = [
                x
                for x in psutil.disk_partitions()
                if x.fstype != "squashfs" and x.mountpoint != "/"
            ]

            # We just have to prompt the user to choose and can't really filter the
            # options
            # The psutil.drive_partitions() function which supposedly can filter by
            # "removable" doesn't seem to work.
            # https://psutil.readthedocs.io/en/latest/#psutil.disk_partitions
            print("\n".join([f"{x.device:<{30}} {x.mountpoint}" for x in mounts]))

            self.usb_path = Prompt.ask(
                "[q]Which mount is the USB stick you would you like to use (or "
                "rescan after inserting the USB sticks to scan again)?[/q]",
                choices=[str(x.mountpoint) for x in mounts] + ["rescan"],
            )
            if self.usb_path != "rescan":
                fstype = [
                    x for x in psutil.disk_partitions() if x.mountpoint == self.usb_path
                ][0].fstype
                if fstype not in SUPPORTED_FILESYSTEMS:
                    print(
                        f"The {self.usb_path} device uses the {fstype} filesystem which"
                        " isn't supported by the offline HSM OS. Choose a different"
                        " device."
                    )
                    self.usb_path = "rescan"
                    continue
                if self.usb_path != self.orchestrator_config.get(
                    "usb_stick_path", []
                ) and Confirm.ask(
                    f"[q]Would you like to save this path ({self.usb_path}) in your"
                    f" hsm-orchestrator config ({self.orchestrator_config_filename})"
                    " for the next time you use the tool?[/q]"
                ):
                    self.orchestrator_config["usb_stick_path"] = self.usb_path
                    self.orchestrator_config.write()
                self.usb_path = Path(self.usb_path)

    def choose_csr(self) -> None | Path:
        """Prompt the user to select a CSR file from the CSR directory.

        :returns: The selected CSR file path, or None if none were found.
        :rtype: Path | None

        """
        csr_list = [x.name for x in self.csr_dir.glob("*.csr")] if self.csr_dir else []
        if len(csr_list) == 1:
            csr_name = csr_list[0]
        elif len(csr_list) == 0:
            return None
        else:
            csr_name = Prompt.ask(
                "[q]Which CSR would you like to use?[/q]", choices=csr_list
            )
        return Path(self.csr_dir / csr_name)

    def generate_instructions(self) -> str:
        """Generate shell instructions for running openssl on the offline HSM server.

        :returns: Instructions string.
        :rtype: str

        """
        # Take a CA_default private_key value like "hwcrhk_rsa-rootcaproductionamo" and
        # set the app name and key ident
        preload_app_name, preload_key_ident = self.openssl_config[
            self.openssl_config["ca"]["default_ca"]
        ]["private_key"].split("_", maxsplit=1)
        batch_mode = True
        # Do we want preload to do --file-logging and capture the output to save? Maybe
        # we don't care given that if preload fails, openssl won't run.
        preload_command = (
            "/opt/nfast/bin/preload"
            f" --appname={preload_app_name} --key-ident={preload_key_ident} /bin/bash"
        )
        openssl_path = "/opt/nfast/bin/openssl"
        # TODO : Do we insert a command here to copy the time from the workstation since
        # the hsm server being airgapped will get out of sync with time slowly? Or get a
        # USB GPS/radio time device
        batch_argument = "  -batch \\" if batch_mode else ""
        instructions = f"""
# Run this command to load the OCS quorum and enter passphrases

cd /root
{preload_command}

# Run this command to sign a certificate

cd /path/to/usb/stick
{openssl_path} ca \\
  -config "{self.cnf_file.name}" \\
  -engine nfkm -keyform engine \\
  -in "{self.csr_file.name}" \\
  -out "{self.csr_file.with_suffix('.crt').name}" \\
{batch_argument}
  -notext \\
  2>&1 | tee "{self.csr_file.with_suffix('.output').name}.txt"

# {self.csr_file.with_suffix('.crt').name} will be created

# Once this is done, you can remove the USB stick from the HSM server and plug
# it back into your laptop and run `hsm-orchestrator pull-from-stick`
"""
        # TODO : Add a listing of the files that are being copied to the USB stick into
        # the instructions.
        return instructions

    def create_list_of_cert_and_artifacts(self, actions, ca_cert_filename_on_usb):
        # Move the newly created certificate, and it's associated artifacts to the
        # certs_issued directory
        if len([x for x in self.usb_path.glob("*.crt") if x not in actions]) == 0:
            print(
                "There aren't any .crt files (other than the CA .crt file) on the USB"
                " stick."
            )
            exit(1)
        result = {}
        for crt_file in self.usb_path.glob("*.crt"):
            if crt_file in actions:
                continue
            expected_cert_files = {
                Path(self.usb_path / crt_file.with_suffix(x))
                for x in (".crt", ".csr", ".cnf", ".output.txt", ".instructions.txt")
            }
            missing_files = expected_cert_files - {x for x in self.usb_path.iterdir()}
            if len(missing_files) > 0:
                print(
                    f"The {crt_file.name} file is missing some of the expected"
                    f" associated files: {[str(x) for x in missing_files]}"
                )
                exit(1)
            certs_issued_destination = (
                self.repo_dir / "certs_issued" / Path(ca_cert_filename_on_usb).stem
            )
            if (
                not certs_issued_destination.exists()
            ) and certs_issued_destination not in actions:
                result.update({certs_issued_destination: "mkdir"})
            result.update({x: certs_issued_destination for x in expected_cert_files})
        return result

    def create_list_of_ca_files(self, certificate_authority_directory):
        # Move the updated CA files to the certificate-authorities directory for that CA
        expected_ca_files = {
            self.usb_path / "index.txt",
            self.usb_path / "serial",
        }
        missing_files = expected_ca_files - {x for x in self.usb_path.iterdir()}
        if len(missing_files) > 0:
            print(f"Some of the expected CA files are missing: {missing_files}")
            exit(1)
        return {x: certificate_authority_directory for x in expected_ca_files}

    def process_usb_files(self, actions):
        # Prompt the user to see if they want to perform all the move and delete actions
        displayed_actions = {}
        for action, destination in actions.items():
            displayed_action = (
                action.relative_to(self.usb_path.parent)
                if isinstance(action, PurePath)
                else action
            )
            displayed_destination = (
                destination.relative_to(self.repo_dir.parent)
                if isinstance(destination, PurePath)
                else destination
            )
            displayed_actions[displayed_action] = displayed_destination
        pad_width = max(
            [len(str(displayed_actions[x])) for x in displayed_actions.keys()]
        )
        print(f"{'Action / Destination':<{pad_width}}   Source File")
        print(
            "\n".join(
                f"{str(displayed_actions[x]):<{pad_width}} : {x}"
                for x in displayed_actions.keys()
            )
        )
        if Confirm.ask("[q]Would you like to perform these actions?[/q]"):
            for filename in actions:
                if actions[filename] == "delete":
                    filename.unlink()
                    print(f"Deleted {filename}")
                elif actions[filename] == "mkdir":
                    filename.mkdir()
                    print(f"Created {filename}")
                elif issubclass(type(actions[filename]), PurePath):
                    destination = Path(actions[filename] / filename.name)
                    shutil.copy2(filename, destination)
                    # We only need to ensure that the execute bit isn't set because
                    # that's all that git records
                    # https://github.com/git/git/commit/e447947
                    destination.chmod(
                        destination.stat().st_mode
                        & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                    )
                    filename.unlink()
                    print(f"Moved {filename} to {actions[filename]}")
                elif actions[filename] == "ignore":
                    print(f"Ignored {filename}")


def set_default_click_arguments_from_config(
    ctx: click.Context, param: click.Parameter, value: Path
) -> Path:
    """Read the configuration file and set click defaults accordingly.

    :param ctx: The Click context.
    :type ctx: click.Context
    :param param: The Click parameter.
    :type param: click.Parameter
    :param value: Path to the configuration file.
    :type value: Path
    :returns: The configuration file path.
    :rtype: Path

    """
    orchestrator_config_file = value
    if orchestrator_config_file.exists():
        orchestrator_config = ConfigObj(infile=str(orchestrator_config_file))
        ctx.default_map = orchestrator_config.dict()
    else:
        orchestrator_config_file.parent.mkdir(parents=True, exist_ok=True)
        orchestrator_config_file.touch()
    return orchestrator_config_file


# https://stackoverflow.com/a/73669230/168874
@click.group("hsm-orchestrator", context_settings={"auto_envvar_prefix": "HSM"})
def main() -> None:
    """Tool for managing the process of interacting with the offline HSM"""
    pass


@main.command("push-to-stick")
@click.option(
    "--config",
    "orchestrator_config_filename",
    default=DEFAULT_CONFIG_FILE,
    type=click.Path(path_type=Path),
    callback=set_default_click_arguments_from_config,
    is_eager=True,
    help=f"The path to a configuration file. (default: {DEFAULT_CONFIG_FILE})",
)
@click.option(
    "--repo-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    callback=validators.validate_repo_dir,
    required=True,
    help="The path to your local hsm git repository",
)
@click.option(
    "--csr-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    callback=validators.validate_csr_dir,
    required=True,
    help="The path to the directory containing the .csr and OpenSSL .cnf files",
)
@click.option(
    "--skip-git-fetch",
    is_flag=True,
    help="Skip performing a git fetch on the repository",
)
def push_to_stick(
    orchestrator_config_filename: Path,
    repo_dir: Path,
    csr_dir: Path,
    skip_git_fetch: bool,
) -> None:
    """Copy .csr and .cnf files to a USB stick along with instructions
    \f

    The instructions will explain what to run on the offline HSM.

    :param orchestrator_config_filename: Path to the configuration file.
    :type orchestrator_config_filename: Path
    :param repo_dir: Path to the git repository.
    :type repo_dir: Path
    :param csr_dir: Path to the CSR directory.
    :type csr_dir: Path
    :param skip_git_fetch: Whether to skip fetching from git.
    :type skip_git_fetch: bool
    :returns: None

    """
    orchestrator = HsmOrchestrator(
        orchestrator_config_filename, repo_dir=repo_dir, csr_dir=csr_dir
    )
    orchestrator.check_environment(skip_git_fetch)
    orchestrator.get_openssl_cnf_config()
    orchestrator.check_update_cnf_file()
    orchestrator.choose_usb_disk()

    instructions = orchestrator.generate_instructions()
    instructions_file = Path(
        orchestrator.usb_path
        / f"{orchestrator.csr_file.with_suffix('.instructions.txt').name}"
    )
    with instructions_file.open("w") as f:
        f.write(instructions)
    # TODO : Add check to see if there are files on the usb stick and how to delete them
    shutil.copy2(
        orchestrator.csr_file, orchestrator.usb_path / orchestrator.csr_file.name
    )
    shutil.copy2(
        orchestrator.cnf_file, orchestrator.usb_path / orchestrator.cnf_file.name
    )
    shutil.copy2(
        orchestrator.local_ca_path / "serial", orchestrator.usb_path / "serial"
    )
    shutil.copy2(
        orchestrator.local_ca_path / "index.txt", orchestrator.usb_path / "index.txt"
    )
    shutil.copy2(
        orchestrator.ca_cert_file,
        orchestrator.usb_path / orchestrator.ca_cert_file.name,
    )
    print(
        f"The instructions and files have been written to {orchestrator.usb_path} USB"
        f" stick. The instructions file is {instructions_file}"
    )


@main.command("pull-from-stick")
@click.option(
    "--config",
    "orchestrator_config_filename",
    default=DEFAULT_CONFIG_FILE,
    type=click.Path(path_type=Path),
    callback=set_default_click_arguments_from_config,
    is_eager=True,
    help=f"The path to a configuration file. (default: {DEFAULT_CONFIG_FILE})",
)
@click.option(
    "--repo-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    callback=validators.validate_repo_dir,
    required=True,
    help="The path to your local hsm git repository",
)
@click.option(
    "--skip-git-fetch",
    is_flag=True,
    help="Skip performing a git fetch on the repository",
)
def pull_from_stick(
    orchestrator_config_filename: Path, repo_dir: Path, skip_git_fetch: bool
) -> None:
    """Pull signed certificates and updated CA files from a USB stick
    \f

    :param orchestrator_config_filename: Path to the configuration file.
    :type orchestrator_config_filename: Path
    :param repo_dir: Path to the git repository.
    :type repo_dir: Path
    :param skip_git_fetch: Whether to skip fetching from git.
    :type skip_git_fetch: bool
    :returns: None

    """
    orchestrator = HsmOrchestrator(orchestrator_config_filename, repo_dir=repo_dir)
    orchestrator.choose_usb_disk()

    actions = {}  # Key is the file and value is the action to perform on that file
    ca_cert_filename_on_usb = orchestrator.get_ca_cert_filename_on_usb()
    certificate_authority_directory = next(
        iter([
            x
            for x in orchestrator.ca_cert_files_in_repo
            if x.name == ca_cert_filename_on_usb
        ])
    ).parent
    # Delete the CA crt file on the USB stick
    actions[Path(orchestrator.usb_path / ca_cert_filename_on_usb)] = "delete"

    actions.update(
        orchestrator.create_list_of_cert_and_artifacts(actions, ca_cert_filename_on_usb)
    )

    actions.update(
        orchestrator.create_list_of_ca_files(certificate_authority_directory)
    )

    directories = {x for x in orchestrator.usb_path.iterdir() if x.is_dir()}
    actions.update({x: "ignore" for x in directories})
    remaining_files = {
        x for x in orchestrator.usb_path.iterdir() if x not in actions.keys()
    }
    actions.update({x: "delete" for x in remaining_files})

    orchestrator.process_usb_files(actions)
    print(
        "Now that the git repo has been updated with the new files, you likely want "
        "to commit those changes, push them to the branch and eventually merge the "
        "branch to main."
    )


@main.command("check")
@click.option(
    "--config",
    "orchestrator_config_filename",
    default=DEFAULT_CONFIG_FILE,
    type=click.Path(path_type=Path),
    callback=set_default_click_arguments_from_config,
    is_eager=True,
    help=f"The path to a configuration file. (default: {DEFAULT_CONFIG_FILE})",
)
@click.option(
    "--repo-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    callback=validators.validate_repo_dir,
    required=True,
    help="The path to your local hsm git repository",
)
@click.option(
    "--csr-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    callback=validators.validate_csr_dir,
    required=True,
    help="The path to the directory containing the .csr and OpenSSL .cnf files",
)
@click.option(
    "--skip-git-fetch",
    is_flag=True,
    help="Skip performing a git fetch on the repository",
)
def check(
    orchestrator_config_filename: Path,
    repo_dir: Path,
    csr_dir: Path,
    skip_git_fetch: bool,
) -> None:
    """Examine the environment and test the .csr and OpenSSL .cnf file
    \f

    :param orchestrator_config_filename: Path to the configuration file.
    :type orchestrator_config_filename: Path
    :param repo_dir: Path to the git repository.
    :type repo_dir: Path
    :param csr_dir: Path to the CSR directory.
    :type csr_dir: Path
    :param skip_git_fetch: Whether to skip fetching from git.
    :type skip_git_fetch: bool
    :returns: None

    """
    orchestrator = HsmOrchestrator(
        orchestrator_config_filename, repo_dir=repo_dir, csr_dir=csr_dir
    )
    orchestrator.check_environment(skip_git_fetch)
    orchestrator.get_openssl_cnf_config()
    orchestrator.check_update_cnf_file()
    orchestrator.check_for_matching_issued_cert()
    print("Check completed.")


if __name__ == "__main__":
    main()
