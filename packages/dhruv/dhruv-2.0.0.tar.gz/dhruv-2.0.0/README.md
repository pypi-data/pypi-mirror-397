# dhruv 🐍

> **A foundational Python package for AI-assisted development, featuring an AI Developer Handbook and batteries-included templates.**

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/dhruv.svg)](https://pypi.org/project/dhruv/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
![Wheel](https://img.shields.io/pypi/wheel/dhruv.svg)
[![Build status](https://github.com/dhruv13x/dhruv/actions/workflows/publish.yml/badge.svg)](https://github.com/dhruv13x/dhruv/actions/workflows/publish.yml)
[![Codecov](https://codecov.io/gh/dhruv13x/dhruv/graph/badge.svg)](https://codecov.io/gh/dhruv13x/dhruv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

</div>

---

## ⚡ Quick Start

### Prerequisites
*   Python 3.8+
*   pip

### Installation
```bash
pip install .
```
*Or for development:*
```bash
pip install -e .
```

### Run
Verify the installation immediately:
```bash
dhruv hello
```

### Demo
Use the core logic in your own scripts:
```python
from dhruv.main import hello

# Access the core functionality directly
print(hello())
# Output: "Hello from Dhruv!"
```

---

## ✨ Features

*   **🧠 AI Developer Handbook**: A comprehensive set of standardized system prompts (`src/dhruv/prompts/`) to guide AI agents through Documentation, Roadmapping, Testing, and Refactoring.
*   **🚀 Modern CLI Foundation**: Built with **Typer** and **Rich** for a robust, beautiful, and self-documenting command-line interface.
*   **📦 Batteries-Included Templates**: Pre-configured templates for `pytest`, project settings, and more, located in `src/dhruv/templates/`.
*   **🏗️ Clean Architecture**: Follows a strict `src` layout with modular design, ensuring scalability and maintainability.
*   **🎨 Visual Utilities**: Includes banner generation and syntax highlighting themes for a polished user experience.

---

## 🛠️ Configuration

### CLI Arguments
The `dhruv` CLI is the primary interface.

| Command | Argument | Description |
| :--- | :--- | :--- |
| `dhruv` | `hello` | Prints a welcome message to verify installation. |
| `dhruv` | `--help` | Show the help message and exit. |

*Note: No environment variables are currently required for core operation.*

---

## 🏗️ Architecture

### Directory Tree
```text
src/
└── dhruv/
    ├── prompts/    # 📘 AI Developer Handbook & System Prompts
    ├── templates/  # 🛠️ Configuration Templates (pytest, settings)
    ├── utils/      # 🔧 Utility modules (banners, themes)
    ├── cli.py      # 🚀 CLI entry point (Typer)
    └── main.py     # 🧠 Core logic
```

### High-Level Flow
1.  **Entry Point**: `dhruv` command triggers `src/dhruv/cli.py`.
2.  **Routing**: `typer` routes commands (e.g., `hello`) to their respective functions.
3.  **Core Logic**: Commands invoke logic in `src/dhruv/main.py` or access resources in `prompts/` and `templates/`.
4.  **Utilities**: `src/dhruv/utils/` provides shared functionality like banner rendering and styling.

---

## 🐞 Troubleshooting

| Issue | Possible Cause | Solution |
| :--- | :--- | :--- |
| `command not found: dhruv` | PATH issue or not installed. | Ensure `pip install .` was successful and your Python scripts folder is in your PATH. |
| `ModuleNotFoundError` | Virtual environment mismatch. | Activate the correct venv where `dhruv` was installed. |

### Debug Mode
If you encounter unexpected behavior, check your Python version and environment details:
```bash
python --version
pip show dhruv
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Dev Setup
1.  Clone the repository.
2.  Install package in editable mode: `pip install -e .`
3.  Install test dependencies: `pip install pytest pytest-cov`
4.  Run tests: `pytest`

---

## 🗺️ Roadmap

*   [x] Initial Release & Core Structure
*   [x] CLI Implementation (`typer`)
*   [x] AI Developer Handbook (Prompts)
*   [ ] **Interactive Init**: `dhruv init` to scaffold new projects.
*   [ ] **Prompt Management**: CLI commands to list and display prompts.
*   [ ] **Template Injection**: Automate copying templates to project root.
