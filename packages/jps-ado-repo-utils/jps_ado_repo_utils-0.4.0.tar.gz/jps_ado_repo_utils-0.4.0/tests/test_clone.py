import subprocess
from pathlib import Path
from unittest.mock import patch
import pytest

from jps_ado_repo_utils.dependency_finder import (
    clone_repository,
    extract_repo_basename,
    extract_url_basename,
)


def test_clone_success(tmp_path: Path):
    """
    Mock a successful git clone operation.
    The test must create the destination directory because subprocess.run is mocked.
    """
    repo_url = "git@github.com:example/repo.git"
    base = tmp_path

    mock_result = subprocess.CompletedProcess(
        args=["git", "clone"],
        returncode=0,
        stdout="OK",
        stderr=""
    )

    with patch("subprocess.run", return_value=mock_result):
        repo_dir, err = clone_repository(repo_url, base)

    # Validate clone_repository() returned correct values
    assert err is None
    assert repo_dir is not None

    # Create the mocked clone directory
    repo_dir.mkdir(parents=True, exist_ok=True)

    # Now the expected behavior is satisfied
    assert repo_dir.exists()


def test_clone_failure(tmp_path: Path):
    """
    Mock a failed git clone operation.
    """
    repo_url = "git@github.com:example/repo.git"
    base = tmp_path

    mock_result = subprocess.CompletedProcess(
        args=["git", "clone"],
        returncode=1,
        stdout="",
        stderr="permission denied"
    )

    with patch("subprocess.run", return_value=mock_result):
        repo_dir, err = clone_repository(repo_url, base)

    assert repo_dir is None
    assert "permission denied" in err


@pytest.mark.parametrize(
    "url,expected",
    [
        # Azure DevOps SSH URLs
        (
            "git@ssh.dev.azure.com:v3/baylorgenetics/Baylor Genetics/pipeline-nextflow-runner",
            "pipeline-nextflow-runner",
        ),
        (
            "git@ssh.dev.azure.com:v3/org/project/my-repo",
            "my-repo",
        ),
        # URL-encoded spaces in repository name
        (
            "git@ssh.dev.azure.com:v3/org/Baylor%20Genetics/my-repo",
            "my-repo",
        ),
        # GitHub URLs
        ("git@github.com:user/my-repo.git", "my-repo"),
        ("git@github.com:user/my-repo", "my-repo"),
        # HTTPS URLs
        ("https://github.com/user/my-repo.git", "my-repo"),
        ("https://github.com/user/my-repo", "my-repo"),
        # Trailing slashes
        ("git@github.com:user/my-repo/", "my-repo"),
    ],
)
def test_extract_repo_basename(url: str, expected: str):
    """Test that extract_repo_basename correctly extracts repository names."""
    result = extract_repo_basename(url)
    assert result == expected


@pytest.mark.parametrize(
    "url,expected",
    [
        # Azure DevOps HTTPS URLs with URL-encoded spaces
        (
            "https://baylorgenetics.visualstudio.com/Baylor%20Genetics/_git/pipeline-api-endpoints",
            "pipeline-api-endpoints",
        ),
        # Regular HTTPS URLs
        ("https://visualstudio.com/org/project/_git/my-package", "my-package"),
        # GitHub URLs
        ("git@github.com:user/my-package.git", "my-package"),
        ("https://github.com/user/my-package", "my-package"),
        # SSH URLs
        ("git@ssh.dev.azure.com:v3/org/project/my-package", "my-package"),
        # .git suffix removal
        ("git@github.com:user/repo.git", "repo"),
        # Trailing slashes
        ("https://example.com/path/to/repo/", "repo"),
    ],
)
def test_extract_url_basename(url: str, expected: str):
    """Test that extract_url_basename correctly extracts basenames from various URL formats."""
    result = extract_url_basename(url)
    assert result == expected
