from pathlib import Path
import pytest

from jps_ado_repo_utils.dependency_finder import scan_repository, scan_gitmodules


def test_scan_finds_project_dependency(repo_with_dependency):
    """Verify that scanner detects dependency inside project file."""
    result = scan_repository(
        repo_url="git@fake/repo1.git",
        repo_dir=repo_with_dependency,
        package="mypkg"
    )

    assert result.found_dependency
    assert any("pyproject.toml" in str(p) for p in result.project_files_with_dependency)


def test_scan_detects_import_only(repo_with_import_only):
    """Verify that scanner detects Python import usage."""
    result = scan_repository(
        repo_url="git@fake/repo2.git",
        repo_dir=repo_with_import_only,
        package="mypkg"
    )

    assert result.found_dependency
    assert len(result.python_files_with_import) > 0
    assert any("main.py" in str(p) for p in result.python_files_with_import)


def test_scan_no_dependency(repo_without_dependency):
    """Verify that scanner correctly reports no dependency."""
    result = scan_repository(
        repo_url="git@fake/repo3.git",
        repo_dir=repo_without_dependency,
        package="mypkg"
    )

    assert not result.found_dependency
    assert len(result.python_files_with_import) == 0
    assert len(result.project_files_with_dependency) == 0


def test_scan_gitmodules_no_files(tmp_path: Path):
    """Verify scan_gitmodules handles repositories without .gitmodules files."""
    summary, matches = scan_gitmodules(tmp_path)
    assert "no .gitmodules files found" in summary
    assert len(matches) == 0


def test_scan_gitmodules_with_matching_package(tmp_path: Path):
    """Verify scan_gitmodules detects submodules matching the package name."""
    # Create a .gitmodules file with a matching submodule
    gitmodules_content = """[submodule "pipeline-api"]
	path = bg/api
	url = https://baylorgenetics.visualstudio.com/Baylor%20Genetics/_git/pipeline-api-endpoints
	branch = main
"""
    gitmodules_path = tmp_path / ".gitmodules"
    gitmodules_path.write_text(gitmodules_content)

    summary, matches = scan_gitmodules(tmp_path, package="pipeline-api-endpoints")
    
    # Verify the summary contains the MATCH indicator
    assert "** MATCH" in summary
    assert "pipeline-api-endpoints" in summary
    assert "bg/api" in summary
    
    # Verify the .gitmodules file was identified as containing a match
    assert len(matches) == 1
    assert matches[0] == gitmodules_path


def test_scan_gitmodules_without_matching_package(tmp_path: Path):
    """Verify scan_gitmodules does not match when package differs."""
    gitmodules_content = """[submodule "other-module"]
	path = other/path
	url = https://example.com/_git/different-package
	branch = main
"""
    gitmodules_path = tmp_path / ".gitmodules"
    gitmodules_path.write_text(gitmodules_content)

    summary, matches = scan_gitmodules(tmp_path, package="pipeline-api-endpoints")
    
    # Verify no match was found
    assert "** MATCH" not in summary
    assert len(matches) == 0
    
    # But the summary should still include the submodule info
    assert "other-module" in summary
    assert "different-package" in summary


def test_scan_gitmodules_multiple_submodules_one_match(tmp_path: Path):
    """Verify scan_gitmodules correctly identifies only matching submodules."""
    gitmodules_content = """[submodule "pipeline-api"]
	path = bg/api
	url = https://visualstudio.com/org/_git/pipeline-api-endpoints
	branch = main

[submodule "other-module"]
	path = other/path
	url = https://example.com/_git/different-package
	branch = develop
"""
    gitmodules_path = tmp_path / ".gitmodules"
    gitmodules_path.write_text(gitmodules_content)

    summary, matches = scan_gitmodules(tmp_path, package="pipeline-api-endpoints")
    
    # Verify only one match
    assert summary.count("** MATCH") == 1
    assert "pipeline-api-endpoints" in summary
    assert "different-package" in summary
    assert len(matches) == 1


def test_scan_repository_with_gitmodule_dependency(tmp_path: Path):
    """Verify scan_repository detects dependencies in .gitmodules files."""
    # Create a repository structure with .gitmodules
    gitmodules_content = """[submodule "pipeline-api"]
	path = bg/api
	url = https://example.com/_git/mypkg
	branch = main
"""
    gitmodules_path = tmp_path / ".gitmodules"
    gitmodules_path.write_text(gitmodules_content)

    result = scan_repository(
        repo_url="git@fake/repo.git",
        repo_dir=tmp_path,
        package="mypkg"
    )

    # Verify the dependency was found via gitmodules
    assert result.found_dependency
    assert len(result.gitmodules_with_dependency) == 1
    assert result.gitmodules_with_dependency[0] == gitmodules_path


def test_scan_repository_gitmodule_no_match(tmp_path: Path):
    """Verify scan_repository doesn't false-positive on non-matching gitmodules."""
    gitmodules_content = """[submodule "other"]
	path = other/path
	url = https://example.com/_git/different-pkg
	branch = main
"""
    gitmodules_path = tmp_path / ".gitmodules"
    gitmodules_path.write_text(gitmodules_content)

    result = scan_repository(
        repo_url="git@fake/repo.git",
        repo_dir=tmp_path,
        package="mypkg"
    )

    # Verify no dependency was found
    assert not result.found_dependency
    assert len(result.gitmodules_with_dependency) == 0


def test_repo_scan_result_found_dependency_includes_gitmodules():
    """Verify RepoScanResult.found_dependency is True when gitmodules contain a match."""
    from jps_ado_repo_utils.dependency_finder import RepoScanResult
    from pathlib import Path
    
    result = RepoScanResult(
        repo_url="git@fake/repo.git",
        local_path=Path("/tmp/repo"),
        gitmodules_with_dependency=[Path("/tmp/repo/.gitmodules")]
    )
    
    # Should be True even without project or Python file matches
    assert result.found_dependency
