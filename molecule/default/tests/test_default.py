"""Testinfra checks for the log mailer role."""


def archive_path(host):
    hostname = host.check_output("hostname -s")
    return f"/tmp/{hostname}_logs.tar.bz2"


def test_archive_created(host):
    archive = host.file(archive_path(host))
    assert archive.is_file
    assert archive.mode == 0o644


def test_archive_holds_logs(host):
    # EL images ship no bzip2 binary, so list the archive with Python.
    listing = host.check_output(
        "python3 -c 'import sys, tarfile; "
        "print(chr(10).join(tarfile.open(sys.argv[1]).getnames()))' %s",
        archive_path(host),
    ).split()
    assert any(name.startswith("log/") for name in listing)
