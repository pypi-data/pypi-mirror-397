# Changelog

## [1.2.0] - 2025-12-17

### Changed

- Change unit test regex comparison of tool output so that errors are clearer. ([#19](https://github.com/mozilla/hsm-orchestrator/pull/19)) (Gene Wood)
- Change minimum Python version to 3.10 ([#28](https://github.com/mozilla/hsm-orchestrator/issues/28)) (Gene Wood)

### Added

- Add a new check if the filenames of the .csr .cnf pair match an existing cert ([#27](https://github.com/mozilla/hsm-orchestrator/pull/27)) (Gene Wood)
- Add a check and fix of filesystem permissions, specifically the execute bits of files on the USB stick ([#25](https://github.com/mozilla/hsm-orchestrator/pull/25)) (Gene Wood)
- Add a check to confirm the USB stick is using a filesystem that the Offline HSM can recognize ([#21](https://github.com/mozilla/hsm-orchestrator/pull/21)) (Gene Wood)
- Add a check for the openssl.cnf setting of `unique_subject=yes` and prompts the user to change it ([#17](https://github.com/mozilla/hsm-orchestrator/pull/17)) (Gene Wood)
- Add a check if the `simple_test` private key is being used and warn the user ([#23](https://github.com/mozilla/hsm-orchestrator/pull/23)) (Gene Wood)
- Add minimum versions for dependencies ([#28](https://github.com/mozilla/hsm-orchestrator/issues/28)) (Gene Wood)

### Fixed

- Fix case where the `certs_issued` directory is missing by creating it ([#24](https://github.com/mozilla/hsm-orchestrator/pull/24)) (Gene Wood)
- Fix overly wide `pull-from-stick` output so it's readable ([#20](https://github.com/mozilla/hsm-orchestrator/pull/20)) (Gene Wood)

## [1.1.0] - 2025-09-19

### Changed

- **Breaking:** Rename `push` and `pull` actions and add post-pull next steps ([#6]( https://github.com/mozilla/hsm-orchestrator/pull/6)) (Gene Wood)

### Added

- Add support for git repos which have an `https` remote instead of `ssh` ([#3](https://github.com/mozilla/hsm-orchestrator/pull/3)) (Gene Wood)

## [1.0.2] - 2025-09-12

_First publish to PyPi._

## [1.0.1] - 2025-09-12

_Initial release._

[1.2.0]: https://github.com/mozilla/hsm-orchestrator/releases/tag/v1.2.0

[1.1.0]: https://github.com/mozilla/hsm-orchestrator/releases/tag/v1.1.0

[1.0.2]: https://github.com/mozilla/hsm-orchestrator/releases/tag/v1.0.2

[1.0.1]: https://github.com/mozilla/hsm-orchestrator/releases/tag/v1.0.1
