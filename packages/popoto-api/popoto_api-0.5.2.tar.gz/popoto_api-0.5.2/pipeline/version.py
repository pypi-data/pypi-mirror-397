import os

def get_version():
    version = "0.0.1"
    tag = os.environ.get("CI_COMMIT_TAG", '')
    # CI_COMMIT_BRANCH is not set in merge request pipelines, use MR source branch as fallback
    ticket_number = os.environ.get("CI_COMMIT_BRANCH", '') or os.environ.get("CI_MERGE_REQUEST_SOURCE_BRANCH_NAME", '')
    pipeline_build = os.environ.get("CI_PIPELINE_ID", '')
    commit_sha = os.environ.get("CI_COMMIT_SHORT_SHA", '')

    if tag:
        version = tag
    elif ticket_number and pipeline_build and commit_sha:
        clean_branch = ticket_number.replace("-", "").replace("_", "")
        version = f"{version}+{clean_branch}.{pipeline_build}.{commit_sha}"
    return version


__version__ = get_version()
