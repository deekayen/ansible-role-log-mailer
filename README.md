Log Mailer
==========

[![CI](https://github.com/deekayen/ansible-role-log-mailer/actions/workflows/ci.yml/badge.svg)](https://github.com/deekayen/ansible-role-log-mailer/actions/workflows/ci.yml) [![Project Status: Concept – Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept.](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept)

Email logs from a remote server. This role is intended for users who would like to do debugging or system diagnosis when they have access to login through an Ansible proxy like Tower or Jenkins, but not by direct SSH.


Role Variables
--------------

```
log_find_path: /var/log
log_archive_format: bz2
log_from: awx@tower.example.com
log_to: log_team@example.com
log_email_host: email-smtp.us-east-1.amazonaws.com
log_email_port: 25
```

Optionally, set SMTP credentials at runtime by setting values for `log_email_username` and `log_email_password`. Otherwise, the role defaults to unauthenticated connections to the SMTP server.


Dependencies
------------

None.

Example Playbook
----------------

    - hosts: all

      vars:
        log_find_path: /var/log/tomcat
        log_email_host: smtp.mailgun.org
        log_email_port: 587
        log_email_username: ansible_user
        log_email_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386337623537613731346334656134326636353639636534323033653265346566346139336233
          3864333165313831643262363532396165303831666263390a383866356162656533653364303830
          36373833323266616533643637306534646137343866666337646532396233636533346664303463
          3934303731323236340a313639616532616331353036616662303937396261613539646561346365
          6137

      roles:
         - deekayen.log_mailer
