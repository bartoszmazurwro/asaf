# Installation

You can install _ASAF_ using the following commands.

For the latest PyPI release:

```bash
pip install asaf
```

For the development version:

```bash
pip install "asaf @ git+https://github.com/bartoszmazurwro/asaf.git"
```

For local development:

```bash
git clone https://github.com/bartoszmazurwro/asaf.git
cd asaf
uv sync --locked --all-extras --dev
uv run pytest
```
