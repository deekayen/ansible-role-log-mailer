# deekayen.log_mailer

[![CI](https://github.com/deekayen/ansible-role-log-mailer/actions/workflows/ci.yml/badge.svg)](https://github.com/deekayen/ansible-role-log-mailer/actions/workflows/ci.yml) [![Ansible Galaxy](https://img.shields.io/badge/galaxy-deekayen.log__mailer-blue.svg)](https://galaxy.ansible.com/ui/standalone/roles/deekayen/log_mailer/) [![Project Status: Concept – Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept.](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept) ![BSD 3-Clause license](https://img.shields.io/badge/license-BSD%203--Clause-blue)

An Ansible role that archives a log directory on a Linux host and e-mails the archive. It is meant for people who can run jobs through an automation controller such as AWX, Ansible Tower, or Jenkins but cannot SSH to the host to read logs themselves.

On the managed host, the role archives `log_find_path` with `community.general.archive` to `/tmp/<hostname>_logs.tar.<log_archive_format>`, where `<hostname>` is `ansible_facts.hostname`. It fetches that file to `logs/<inventory_hostname>/tmp/` next to the playbook on the controller. The controller then sends it as an attachment through `community.general.mail` and deletes its local copy.

The Galaxy name is `deekayen.log_mailer`, with an underscore, while the repository is `ansible-role-log-mailer`.

## Requirements

- ansible-core 2.15 or newer on the controller.
- The `community.general` collection on the controller: `ansible-galaxy collection install community.general`.
- SMTP access from the controller to `log_email_host`. The mail, find, and cleanup tasks run on the controller through `delegate_to: localhost`.
- Fact gathering left on. The archive name and the message use `ansible_facts.hostname` and `ansible_facts.fqdn`.
- Privilege escalation on the target if `log_find_path` holds root-owned files, as `/var/log` does. The controller-side tasks set `become: false`, so a play with `become: true` does not try sudo on the controller.

## Supported platforms

`meta/main.yml` declares GenericLinux, all versions. CI runs Molecule against `rockylinux9`, `rockylinux10`, `amazonlinux2023`, `ubuntu2204`, `ubuntu2404`, `ubuntu2604`, `debian12`, and `debian13`, with the e-mail step skipped.

## Installation

From Ansible Galaxy:

```bash
ansible-galaxy role install deekayen.log_mailer
ansible-galaxy collection install community.general
```

Or pin it in `requirements.yml`:

```yaml
---
roles:
  - name: deekayen.log_mailer
    src: https://github.com/deekayen/ansible-role-log-mailer.git
    scm: git
    version: main

collections:
  - name: community.general
```

```bash
ansible-galaxy install -r requirements.yml
```

## Role variables

| Variable | Default | Description |
| --- | --- | --- |
| `log_find_path` | `/var/log` | Directory on the managed host to archive, recursively. Must be an absolute path; the role asserts this. |
| `log_archive_format` | `bz2` | Format passed to `community.general.archive`. The argument spec allows `bz2`, `gz`, `xz`, `tar`, and `zip`. |
| `log_from` | `awx@tower.example.com` | Sender address. Must contain one `@`; the role asserts this. |
| `log_to` | `log_team@example.com` | Recipient address. The assert accepts one address only, so a comma-separated list fails. |
| `log_email_host` | `email-smtp.us-east-1.amazonaws.com` | SMTP server the controller sends through. |
| `log_email_port` | `25` | SMTP server port, 1 to 65535. |

The `log_from` and `log_to` defaults are `example.com` placeholders, so set both. Two optional variables have no default: `log_email_username` and `log_email_password`. When they are unset the role connects to the SMTP server without authentication. Keep the password in Ansible Vault or a secrets lookup.

## Behavior

- Every run archives the current logs and sends them, so a second run always reports changes.
- The archive stays in `/tmp` on the managed host after the run. Only the controller copy is deleted, and the empty `logs/<inventory_hostname>/tmp/` directories stay on the controller.
- The whole of `log_find_path` goes into one attachment. Check the archive size against your mail server's message limit before pointing the role at a large directory.

## Dependencies

None. The `community.general` collection is a requirement, not a role dependency.

## Example playbook

Mail a Tomcat log directory through an authenticated relay:

```yaml
---
- name: E-mail Tomcat logs to the application team.
  hosts: tomcat_servers
  become: true

  vars:
    log_find_path: /var/log/tomcat
    log_from: ansible@example.internal
    log_to: app-team@example.internal
    log_email_host: smtp.example.internal
    log_email_port: 587
    log_email_username: ansible-relay
    log_email_password: "{{ vault_smtp_password }}"

  roles:
    - deekayen.log_mailer
```

The `example.internal` addresses and host are placeholders, and `vault_smtp_password` is a placeholder for a vaulted variable.

## Tags

| Tag | Tasks |
| --- | --- |
| `mail` | The e-mail task. `--skip-tags mail` still archives, fetches, and deletes the controller copy, which leaves only the archive in `/tmp` on the managed host. |

Input validation in `tasks/assert.yml` is tagged `always`.

## Known issues

- `tasks/main.yml:9` names the archive `<hostname>_logs.tar.<log_archive_format>`. With `zip` or `tar` the file is named `.tar.zip` or `.tar.tar`.

## Development

CI runs on every push to `main` and every pull request (see `.github/workflows/ci.yml`):

1. Lint: installs `molecule/default/requirements.yml`, then runs `ansible-lint --profile production` and `flake8 molecule/`.
2. Molecule: converge and testinfra verification in Docker against each distribution listed under [Supported platforms](#supported-platforms).

`molecule/default/molecule.yml` sets `ANSIBLE_SKIP_TAGS: mail`, since the containers have no SMTP server. It also replaces the default test sequence with one that has no idempotence step, because every run creates a new archive.

To run the same checks locally with Docker available:

```bash
pip3 install ansible-core ansible-lint flake8 molecule "molecule-plugins[docker]" docker pytest-testinfra
ansible-galaxy install -r molecule/default/requirements.yml
ansible-lint --profile production
flake8 molecule/
MOLECULE_DISTRO=rockylinux9 molecule test
```

`MOLECULE_DISTRO` selects a `geerlingguy/docker-<distro>-ansible` image. The testinfra checks in `molecule/default/tests/test_default.py` confirm that `/tmp/<hostname>_logs.tar.bz2` exists with mode `0644` and that it contains entries under `log/`.

The repository also has a `.pre-commit-config.yaml`; run `pre-commit run --all-files` before pushing.

### Repository layout

| Path | Purpose |
| --- | --- |
| `tasks/main.yml` | Archive, fetch, find, mail, and controller cleanup. |
| `tasks/assert.yml` | Input validation, tagged `always`. |
| `defaults/main.yml` | Every user-facing variable with a default. |
| `meta/argument_specs.yml` | Argument spec, including the two optional SMTP credentials. |
| `molecule/default/` | Molecule scenario: `molecule.yml`, `prepare.yml`, `converge.yml`, `requirements.yml`, and testinfra tests. |
| `.github/workflows/` | `ci.yml` for lint and Molecule, `release.yml` for Galaxy import. |

## Releases

Pushing a git tag runs `.github/workflows/release.yml`, which imports the tagged commit into Ansible Galaxy as `deekayen.log_mailer`. The import needs a `GALAXY_API_KEY` repository or organization secret.

## License

BSD 3-Clause. See [LICENSE](LICENSE).

## Author

[David Norman](https://github.com/deekayen). Sponsorship links are in [.github/FUNDING.yml](.github/FUNDING.yml).
