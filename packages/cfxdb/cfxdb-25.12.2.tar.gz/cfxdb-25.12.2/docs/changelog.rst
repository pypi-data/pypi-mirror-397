Changelog
=========

This document contains a reverse-chronological list of changes to cfxdb.

.. note::

    For detailed release information including artifacts,
    see :doc:`releases`.

Unreleased
----------

*No unreleased changes yet.*

25.12.2 (2025-12-15)
--------------------

**New**

* Added ``generate-release-notes`` justfile recipe for documentation integration
* Added ``docs-integrate-github-release`` justfile recipe with chain-of-custody files
* Added ``.github/workflows/README.md`` documenting CI/CD architecture
* Added ``release-post-comment.yml`` workflow for GitHub Discussions notifications

**Fix**

* Fixed autoapi duplicate object warnings by adding suppress_warnings in conf.py (#82)
* Consolidated ``download-github-release`` recipe to use ``/tmp/release-artifacts/<tag>`` path
* Fixed release workflow to properly upload wheels (corrected check-release-fileset parameters)
* Fixed OpenSSL checksum format handling in download-github-release recipe
* Aligned download-github-release recipe with autobahn-python/zlmdb for consistency

**Other**

* Updated dependencies: autobahn[all]>=25.12.2, zlmdb>=25.12.2
* Removed tox from dev dependencies (no longer used)
* Added documentation for WHY both zlmdb and autobahn dependencies are needed (#112)

25.12.1 (2025-12-10)
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

* Fixed flatbuffers import: now uses zlmdb's vendored flatbuffers via ``from zlmdb import flatbuffers``
* Fixed import sorting (I001) errors across all source files
* Excluded generated code (``src/cfxdb/gen``) from ruff linting

**Other**

* Updated dependencies: autobahn>=25.12.1, zlmdb>=25.12.1
* Added Python 3.11, 3.12, 3.13, 3.14 support in CI
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
