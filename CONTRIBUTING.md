# Contributing to ASAF

Thank you for considering a contribution to ASAF. The project is still young, so small fixes, tests, clearer docs, and
bug reports are all valuable.

## Development setup

ASAF uses [`uv`](https://docs.astral.sh/uv/) for dependency management and local development.

```bash
git clone https://github.com/bartoszmazurwro/asaf.git
cd asaf
uv sync --locked --all-extras --dev
```

Run the test suite with:

```bash
uv run pytest
```

Run linting and formatting checks with:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
```

Build the documentation locally with:

```bash
uv run mkdocs serve
```

Build the package locally with:

```bash
uv build
```

The built wheel and source distribution will be written to `dist/`.

## Pull requests

Before opening a pull request, please:

- Add or update tests for behavior changes.
- Run `uv run pytest`.
- Run `uv run ruff check src tests`.
- Run `uv run ruff format --check src tests`.
- Update `CHANGELOG.md` for user-facing changes.

Keep pull requests focused. A small, well-tested fix is much easier to review than a broad refactor mixed with behavior
changes.

## Reporting bugs

When reporting a bug, include:

- The ASAF version.
- Your Python version and operating system.
- A minimal code example or input file that reproduces the issue.
- The full traceback, if there is one.

## Release process

Releases are intentionally manual for now.

1. Update `version` in `pyproject.toml`.
2. Move relevant entries from `CHANGELOG.md` under the new version heading.
3. Commit the release changes.
4. Create and push a tag matching the version, for example `v0.0.1`.
5. The `release` GitHub Actions workflow builds the package and publishes it to PyPI.

PyPI publishing is designed to use Trusted Publishing. Before the first release, configure a PyPI trusted publisher for
this repository, workflow file `.github/workflows/release.yml`, and environment `pypi`.
