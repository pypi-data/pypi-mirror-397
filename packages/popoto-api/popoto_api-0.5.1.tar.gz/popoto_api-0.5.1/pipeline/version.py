import os

def get_version():
    version = "0.0.1"
    tag = os.environ.get("CI_COMMIT_TAG", '')
    ticket_number = os.environ.get("CI_COMMIT_BRANCH", '')
    pipeline_build = os.environ.get("CI_PIPELINE_ID", '')

    if tag:
        version = tag
    elif ticket_number:
        clean_branch = ticket_number.replace("-", "").replace("_", "")
        version = f"{version}+{clean_branch}.{pipeline_build}"
    return version


__version__ = get_version()
