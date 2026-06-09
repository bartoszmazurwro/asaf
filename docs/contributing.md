# Contributing

ASAF uses `uv` for dependency management, testing, packaging, and documentation tasks.

## Local setup

```bash
git clone https://github.com/bartoszmazurwro/asaf.git
cd asaf
uv sync --locked --all-extras --dev
```

## Checks

Run tests:

```bash
uv run pytest
```

Run linting and formatting checks:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
```

Build the documentation:

```bash
uv run mkdocs build
```

Build the package:

```bash
uv build
```

## Pull requests

Please include tests for behavior changes and update `CHANGELOG.md` for user-facing changes.

## Releases

Releases are made manually by updating `version` in `pyproject.toml`, updating `CHANGELOG.md`, and pushing a tag such as
`v0.0.1`. The GitHub Actions release workflow then builds and publishes the package to PyPI.
