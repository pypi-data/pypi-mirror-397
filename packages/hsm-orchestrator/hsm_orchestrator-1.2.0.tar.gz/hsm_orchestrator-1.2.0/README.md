# HSM Orchestrator

The **HSM Orchestrator** is a command-line tool for interacting with the offline Hardware Security Module (HSM).

It provides commands to:

* Check **CSR `.csr`** and **OpenSSL configuration `.cnf`** files for validity.
* Push the necessary files to a USB stick for transfer to an offline HSM.
* Pull back the signed certificate and updated Certificate Authority (CA) files from a USB stick.

[![PyPI - Version](https://img.shields.io/pypi/v/hsm-orchestrator)](https://pypi.org/project/hsm-orchestrator/) [![Tests](https://github.com/mozilla/hsm-orchestrator/actions/workflows/tests.yml/badge.svg)](https://github.com/mozilla/hsm-orchestrator/actions/workflows/tests.yml) [![Common Changelog](https://common-changelog.org/badge.svg)](https://common-changelog.org)

---

## Installation

As hsm-orchestrator is a command line tool, the easiest way to install it is using [pipx](https://pipx.pypa.io/stable/).
pipx is a tool to help you install and run end-user applications written in Python. It's roughly similar to macOS's
brew and Linux's apt.

Simple instructions for installing pipx on macOS, various distributions of Linux and Windows can be found here :
https://pipx.pypa.io/stable/#install-pipx

Once pipx is installed, you can install hsm-orchestrator by running

`pipx install hsm-orchestrator`

Note : You don't need to install this as the root user (on macOS or Linux)

You can also install the tool using `pip` into a `virtualenv` or using `pip install --user` into the Python user
install directory.

---

## Configuration

### `config.ini` File Location

By default, the hsm-orchestrator stores configuration at:

* **Linux**: `~/.config/hsm-orchestrator/config.ini`
* **macOS**: `~/Library/Application Support/hsm-orchestrator/config.ini`
* **Windows**: `%LOCALAPPDATA%\Mozilla\hsm-orchestrator\config.ini`

You may need to create the `hsm-orchestrator` directory in order to create the `config.ini` within it.

### `config.ini` Contents

Within that `config.ini` file, you can indicate the location of your local [
`mozilla-services/hsm`](https://github.com/mozilla-services/hsm) git repo
and the `csrs` directory within it.

For example if the path to your local `mozilla-services/hsm` repo on your macOS workstation was `~/Documents/hsm`,
then you could create a `~/Library/Application Support/hsm-orchestrator/config.ini` file with the contents of

```ini
repo_dir = /Users/username/Documents/hsm
csr_dir = /Users/username/Documents/hsm/csrs
```

Adding these values to the config means you don't have to pass them on the command line every time you run
hsm-orchestrator.

---

## Usage

If you've used pipx to install hsm-orchestrator, then the `hsm-orchestrator` tool will be in your PATH and can be
run from anywhere.

If you've configured the tool by creating a `config.ini` file, you don't need to pass the `--repo-dir /path/to/hsm/repo`
and `--csr-dir /path/to/csrs` arguments.

### `check`

`hsm-orchestrator check`

This will perform checks of the environment and your `.csr` and `.cnf` files to make sure that everything is setup
correctly.

### `push-to-stick`

`hsm-orchestrator push-to-stick`

This will first check the environment and files, then copy the `.csr`, `.cnf` and the certificate authority files to a
USB stick along with an instructions text file on what to do on the offline HSM.

### On the Offline HSM

Once you've plugged the USB stick into the offline HSM, you can display the instructions file with a command like

`cat *.instructions.txt`

These instructions will explain what commands to run to operate the offline HSM.

### `pull-from-stick`

`hsm-orchestrator pull-from-stick`

After operating the offline HSM and plugging the USB stick back into your workstation, the pull-from-stick command will
move the files off of the USB stick and into the correct directories in the hsm git repo.

## Requirements

* **Python** ≥ 3.10
* Dependencies (installed automatically):

    * [click](https://click.palletsprojects.com/) for CLI arguments
    * [rich](https://rich.readthedocs.io/) for CLI interaction
    * [configobj](https://configobj.readthedocs.io/) for parsing the orchestrator config file and OpenSSl `.cnf` files
    * [gitpython](https://gitpython.readthedocs.io/) for interacting with the hsm git repo
    * [psutil](https://psutil.readthedocs.io/) for interacting with the removable USB stick
    * [platformdirs](https://platformdirs.readthedocs.io/) for platform agnostic config file locations

---

## Example Workflow

1. Create a new `.csr` + `.cnf` file in the [`csrs`](https://github.com/mozilla-services/hsm/tree/main/csrs) directory
   of the `hsm` git repo.
    * In the `.cnf` file, the `certs`, `database`, `new_certs_dir`, `certificate` and `serial` settings in the
      default_ca section (often called `CA_default`) are relative paths pointing to the current working directory. For
      example, `serial` should have a value like `./serial` or `$dir/serial` where `$dir` is set elsewhere to `.`.
    * In the `.cnf` file, the `certificate` setting should have the value of the CA certificate `.crt` filename in the
      `hsm` git repo's
      [`certificate-authorities`](https://github.com/mozilla-services/hsm/tree/main/certificate-authorities)
      tree.
    * In the `.cnf` file, the `private_key` setting should have the value of the offline HSM application key name
      (instead of a filename as is typically the case). The names of the offline HSM application key names can be found
      in the form of the directory names in the
      [`certificate-authorities`](https://github.com/mozilla-services/hsm/tree/main/certificate-authorities) directory
      in the `hsm` git repo.
2. Run `hsm-orchestrator check` to check the settings in the `.cnf` file and the environment.
3. Insert a blank USB stick in your workstation.
4. Run `hsm-orchestartor push-to-stick` to push the files from the `hsm` git repo to the USB stick.
5. Unmount/eject the USB stick from your workstation and plug the stick into the offline HSM.
6. On the offline HSM, show the instructions by running `cat *.instructions.txt` in the USB stick's directory.
7. Run the commands described in the instructions. It's easiest to copy and paste them.
8. Unmount/eject the USB stick from the offline HSM and plug the stick back into your workstation.
9. Run `hsm-orchestrator pull-from-stick` to move the signed certificate and update the CA files in the `hsm` git repo.

---

# Design Goals

The hsm-orchestrator was created to improve on the
[previous tool](https://github.com/mozilla-services/hsm/blob/72bf80c5812c9aa07c2a633872e014de0c86ac20/hsm).

* The process should not involve copying executable scripts onto the offline HSM server
  as this would be a pathway through which malware could cross the air gap
* Anything to be executed on the offline HSM servers should be conveyed as instructions
  that can be clearly read an interpreted by the operator each time to prevent malware
* Protections should be made to prevent the instructions which the operator follows on the
  offline HSM from containing malware via methods like [Trojan Source](https://en.wikipedia.org/wiki/Trojan_Source)
  or whitespace hiding executable text off the side of the screen.
* Everything about the actions taken on the offline HSM should be captured along with the
  `.csr` and certificate to make the process deterministically reproducible. This artifact collection
  which would include the `.csr`, `.cnf` file, the instructions, the output from the openssl run
  and the certificate produced. All of these artifacts should be committed to the `hsm` repo.
* Foreign files (`.csr`, `.cnf`, `ca.crt` etc) should stay on the USB stick. No reason to move files onto
  and off of the offline HSM server
* There should be three functions
    * Validate an `openssl.cnf` file and guide the user through customizing the file.
      This is meant for use by the autograph team
    * Push files and commands across the airgap
    * Pull resulting certificates back across
      the airgap.
* Use `click` for processing arguments and `rich` for console output
* Perform checks to detect any risky situations. Over time as we discover new ways to do things wrong
  we should extend the tool to check for those newly encountered problems.
* Don't have the tool get involved in commiting to the git repo or pushing to the remote. Historically
  we spent much more time dealing with commits and pushes that we didn't want than if we had
  just done the commits and pushes ourselves.
* Look for `.csr` files in a specific location instead of doing a `find` across a large area of the `hsm`
  repo

# Possible Future Features

* Do we want to convey time from the workstation to the air gapped HSM server? Or just get
  a GPS time source : https://mozilla-hub.atlassian.net/browse/INFRASEC-1459
* Check the filesystem on the USB stick to ensure it's one which will work on the offline HSM server.
  Maybe we enforce using the UDF filesystem as that should work on all platforms? Maybe bar usage of FAT32?
* Echo the date/time that the signing took place into the output. As the time on the offline HSM drifts
  the benefit of recording this timestamp may decrease.
* We could create a `configobj.InterpolationEngine` like `TemplateInterpolation` but for OpenSSL syntax
    * https://docs.openssl.org/3.1/man5/config/#settings
    * This would remove $$ = $ and add support for [`dollarid`](https://docs.openssl.org/3.1/man5/config/#directives)
      and [`.include`](https://docs.openssl.org/3.1/man5/config/#directives)
