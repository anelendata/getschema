# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/daigotanaka/getschema/issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

getschema could always use more documentation, whether as part of the
official README.md, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/daigotanaka/getschema/issues.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Submit a pull request through the GitHub website.

### Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.

3. The pull request should pass the `tests` GitHub Actions workflow
   (`pytest tests` on Python 3.9-3.12). Run it locally with
   `uv run --project . pytest -q tests`.

## Releasing (maintainers)

Releases publish to PyPI as [`getschema`](https://pypi.org/project/getschema/)
via GitHub Actions **Trusted Publishing** (OIDC) — no API token is stored in the
repo. To cut a release:

1. Add a new section at the top of [`HISTORY.md`](HISTORY.md) for the version.
2. Bump `version` in `pyproject.toml`.
3. Commit both.
4. Tag and push:

   ```bash
   git push origin main
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

   The `v*` tag triggers `.github/workflows/release.yml`: build -> smoke
   (install the wheel and the sdist in a clean venv, check the version, run the
   `getschema` CLI on a sample file, run `tests` against the installed package)
   -> publish -> verify (install the published version from PyPI). Approve the
   `pypi` environment deployment if GitHub prompts.

Notes:

- **PyPI versions are immutable.** A version can never be re-uploaded, so a
  broken build means bumping to the next patch — never reusing a number.
- Keep the tag and `pyproject.toml` `version` in sync (`vX.Y.Z` <-> `X.Y.Z`); the
  build job fails when they differ.

One-time setup (needed before the first automated release):

- On PyPI, project `getschema` -> Settings -> Publishing -> add a GitHub trusted
  publisher: owner `anelendata`, repository `getschema`, workflow `release.yml`,
  environment `pypi`.
- On GitHub, repository Settings -> Environments -> create `pypi` (optionally with
  required reviewers so each publish needs an approval).
