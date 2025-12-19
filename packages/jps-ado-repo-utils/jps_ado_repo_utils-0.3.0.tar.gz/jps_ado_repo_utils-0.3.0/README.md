# jps-ado-repo-utils

![Build](https://github.com/jai-python3/jps-ado-repo-utils/actions/workflows/test.yml/badge.svg)
![Publish to PyPI](https://github.com/jai-python3/jps-ado-repo-utils/actions/workflows/publish-to-pypi.yml/badge.svg)
[![codecov](https://codecov.io/gh/jai-python3/jps-ado-repo-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/jai-python3/jps-ado-repo-utils)

Utils for managing Azure DevOps code repositories

## 🚀 Overview

`jps-ado-repo-utils` is a Python utility for scanning multiple git repositories to identify dependencies on specific Python packages. It's particularly useful for managing large codebases across multiple repositories in Azure DevOps environments.

The tool clones repositories, analyzes both project configuration files (like `pyproject.toml`, `setup.py`, `requirements.txt`) and Python source files for import statements, then generates comprehensive reports on where dependencies are found.

### Features

✨ **Parallel Processing** — Scan multiple repositories concurrently with configurable worker threads

🔍 **Comprehensive Scanning** — Detects dependencies in:
- Project configuration files (`pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `Pipfile`)
- Python source files (import statements)
- Git submodules (`.gitmodules`)

📊 **Detailed Reporting** — Generates structured reports with:
- Successfully scanned repositories
- Repositories with found dependencies
- Repositories without dependencies
- Failed git clone operations
- Scan errors with detailed diagnostics

🔒 **SSH Support** — Designed for Azure DevOps SSH URLs

📝 **Structured Logging** — Comprehensive logging with timestamps and severity levels

### Example Usage

```bash
# Install the package
pip install jps-ado-repo-utils

# Scan repositories for a specific package dependency
jps-ado-repo-utils-dependency-finder \
    --infile repos.txt \
    --package my-package-name \
    --max-workers 10
```

Create a `repos.txt` file with one repository URL per line:
```text
git@vs-ssh.visualstudio.com:v3/org/project/repo1
git@vs-ssh.visualstudio.com:v3/org/project/repo2
git@vs-ssh.visualstudio.com:v3/org/project/repo3
```

The tool will generate:
- A detailed log file tracking all operations
- A comprehensive report showing which repositories use the specified package

For detailed usage instructions, see [USAGE.md](docs/USAGE.md).

## 📦 Installation

```bash
make install
```

## 🧪 Development

```bash
make fix && make format && make lint
make test
```

## 📜 License

MIT License © Jaideep Sundaram
