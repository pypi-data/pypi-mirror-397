from pathlib import Path
import pytest

from jps_ado_repo_utils.dependency_finder import write_report, RepoScanResult, CloneFailure, ScanFailure


def test_report_format(tmp_path: Path):
    """Verify that all required sections appear in the correct order."""
    report_file = tmp_path / "report.txt"

    # Dummy successful scan result
    r = RepoScanResult(
        repo_url="git@a/repo.git",
        local_path=tmp_path / "repo",
        project_files_scanned=[],
        python_files_scanned=[],
    )

    clone_failures = [
        CloneFailure(repo_url="git@fail/repo1.git", error_message="permission denied")
    ]

    scan_failures = [
        ScanFailure(repo_url="git@fail/repo2.git", local_path=tmp_path, error_message="unexpected error")
    ]

    write_report(report_file, results=[r], clone_failures=clone_failures, scan_failures=scan_failures)

    text = report_file.read_text()

    # Sections must appear
    assert "Failed Git Clone" in text
    assert "Scanned Repositories" in text
    assert "Found Dependency" in text
    assert "Dependency Not Found" in text
    assert "Scan Errors" in text

    # Clone failure formatting
    assert "git@fail/repo1.git" in text
    assert "permission denied" in text

    # Scan error formatting
    assert "git@fail/repo2.git" in text
    assert "unexpected error" in text


def test_report_includes_gitmodules(tmp_path: Path):
    """Verify that gitmodules matches appear in the report."""
    report_file = tmp_path / "report.txt"
    
    # Create a result with gitmodule dependency
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    gitmodules_path = repo_dir / ".gitmodules"
    gitmodules_path.write_text("[submodule \\\"test\\\"]\\nurl=example\\n")
    
    r = RepoScanResult(
        repo_url="git@a/repo.git",
        local_path=repo_dir,
        gitmodules_with_dependency=[gitmodules_path],
    )

    write_report(report_file, results=[r], clone_failures=[], scan_failures=[])
    
    text = report_file.read_text()
    
    # Verify gitmodules section appears in "Found Dependency"
    assert "Git submodules with matching URL" in text
    assert ".gitmodules" in text
