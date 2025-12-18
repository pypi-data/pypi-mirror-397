Changelog
=========

This document contains a reverse-chronological list of changes to wamp-xbr.

.. note::

    For detailed release information including artifacts,
    see :doc:`releases`.

Unreleased
----------

*No unreleased changes yet.*

25.12.2 (2025-12-17)
--------------------

**New**

* Added comprehensive smoke tests for wheel and sdist installation verification (#168)
* Added ``test-wheel-install`` and ``test-sdist-install`` recipes for CI verification
* Added Python 3.14 support to test matrix and classifiers

**Fix**

* Fixed wheel missing ``xbr/abi/`` directory with compiled Solidity ABIs (#168)
* Fixed yapf import for Python 3.13+ compatibility (lib2to3 was removed)
* Fixed CI to verify final built wheel in clean, separate venv (#168)

**Other**

* Updated zlmdb dependency to >=25.12.3 (fixes FlatBuffers reflection imports)
* Added verify job to main.yml workflow for distribution testing

25.12.1 (2025-12-16)
--------------------

**New**

* Modernized build system: migrated from setup.py to pyproject.toml with hatch backend
* Added comprehensive just recipes for development workflow (create, install-dev, check, test, docs, dist)
* Added uv for fast Python environment management
* Added ruff for code formatting and linting (replaces flake8/black)
* Added ty (Astral) for type checking
* Added Sphinx documentation with MyST Markdown support and furo theme
* Added sphinx-autoapi for automatic API documentation generation
* Modernized CI/CD workflows with chain-of-custody verification using wamp-cicd reusable actions

**Fix**

* Fixed import sorting (I001) errors across source files
* Fixed documentation build configuration for Read the Docs
* Fixed release.yml workflow check-release-fileset parameters (wheel was missing from releases)
* Aligned justfile download-github-release recipe with autobahn-python/zlmdb/cfxdb
* Synced package.json version with pyproject.toml (was 21.4.1)

**Other**

* Updated dependencies: autobahn>=25.12.2, txaio>=25.12.2, zlmdb>=25.12.2
* Rewrote download-github-release recipe to use curl (no gh auth required)
* Added Python 3.11, 3.12, 3.13 support in CI
* Dropped Python 3.9, 3.10 support (minimum is now Python 3.11)

..
    Format for entries:

    vX.Y.Z (YYYY-MM-DD)
    -------------------

    **New**

    * Description of new feature (#issue)

    **Fix**

    * Description of bug fix (#issue)

    **Other**

    * Description of other changes (#issue)
