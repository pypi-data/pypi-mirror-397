# hello-world

A lightweight Python project template for building and testing simple packages.

## Project goals

- Provide a minimal, easy-to-understand Python package layout.
- Keep dependencies and setup lightweight.
- Offer a clear path for contributing and releasing.

## Installation

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Using conda

```bash
conda create -n structflo python=3.11
conda activate structflo
pip install -e .
```

## Usage

```python
from structflo.helloworld import helloworld

print(helloworld())
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and release guidance.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
