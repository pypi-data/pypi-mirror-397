#!/usr/bin/env python3
# Copyright (c) typedef int GmbH, Germany, 2025. All rights reserved.
#
# Smoke tests for cfxdb package verification.
# Used by CI to verify wheels and sdists actually work after building.

"""
Smoke tests for cfxdb package.

This script verifies that a cfxdb installation is functional by testing:
1. Import cfxdb and check version
2. Import zlmdb (dependency) and verify vendored flatbuffers
3. Import autobahn (dependency) and check version
4. Import cfxdb database schemas and verify they load
5. Verify .fbs schema files are bundled
6. Verify .bfbs binary schema files are bundled

ALL TESTS ARE REQUIRED. Both wheel installs and sdist installs MUST
provide identical functionality.
"""

import sys
from pathlib import Path


def test_import_cfxdb():
    """Test 1: Import cfxdb and check version."""
    print("Test 1: Importing cfxdb and checking version...")
    try:
        import cfxdb
        print(f"  cfxdb version: {cfxdb.__version__}")
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import cfxdb: {e}")
        return False


def test_import_zlmdb():
    """Test 2: Import zlmdb (dependency) and verify vendored flatbuffers."""
    print("Test 2: Importing zlmdb and verifying vendored flatbuffers...")
    try:
        import zlmdb
        print(f"  zlmdb version: {zlmdb.__version__}")

        # Verify cfxdb uses zlmdb's vendored flatbuffers
        from zlmdb import flatbuffers
        print(f"  zlmdb.flatbuffers: available")
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import zlmdb: {e}")
        return False


def test_import_autobahn():
    """Test 3: Import autobahn (dependency) and check version."""
    print("Test 3: Importing autobahn and checking version...")
    try:
        import autobahn
        print(f"  autobahn version: {autobahn.__version__}")
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import autobahn: {e}")
        return False


def test_import_schemas():
    """Test 4: Import cfxdb database schemas and verify they load."""
    print("Test 4: Importing cfxdb database schemas...")
    try:
        # Import main schema modules
        from cfxdb import globalschema, mrealmschema
        print("  globalschema: imported")
        print("  mrealmschema: imported")

        # Import specific schema modules
        from cfxdb.realmstore import RealmStore
        from cfxdb.user import User
        from cfxdb.mrealm import ManagementRealm
        print("  RealmStore, User, ManagementRealm: imported")

        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import schemas: {e}")
        return False


def test_fbs_files():
    """Test 5: Verify .fbs schema files are bundled."""
    print("Test 5: Verifying .fbs schema files are bundled...")
    try:
        import cfxdb
        cfxdb_path = Path(cfxdb.__file__).parent

        # Expected .fbs files
        expected_fbs = [
            "arealm.fbs",
            "common.fbs",
            "cookiestore.fbs",
            "log.fbs",
            "meta.fbs",
            "mrealm.fbs",
            "realmstore.fbs",
            "reflection.fbs",
            "user.fbs",
            "xbr.fbs",
            "xbrmm.fbs",
            "xbrnetwork.fbs",
        ]

        found = []
        missing = []
        for fbs in expected_fbs:
            fbs_path = cfxdb_path / fbs
            if fbs_path.exists():
                found.append(fbs)
            else:
                missing.append(fbs)

        print(f"  Found {len(found)}/{len(expected_fbs)} .fbs files")
        if missing:
            print(f"  Missing: {', '.join(missing)}")
            print("  FAIL")
            return False
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Error checking .fbs files: {e}")
        return False


def test_bfbs_files():
    """Test 6: Verify .bfbs binary schema files are bundled."""
    print("Test 6: Verifying .bfbs binary schema files are bundled...")
    try:
        import cfxdb
        cfxdb_path = Path(cfxdb.__file__).parent
        gen_path = cfxdb_path / "gen"

        # Expected .bfbs files (in gen/ directory)
        expected_bfbs = [
            "arealm.bfbs",
            "common.bfbs",
            "cookiestore.bfbs",
            "log.bfbs",
            "meta.bfbs",
            "mrealm.bfbs",
            "realmstore.bfbs",
            "reflection.bfbs",
            "user.bfbs",
            "xbr.bfbs",
            "xbrmm.bfbs",
            "xbrnetwork.bfbs",
        ]

        found = []
        missing = []
        for bfbs in expected_bfbs:
            bfbs_path = gen_path / bfbs
            if bfbs_path.exists():
                found.append(bfbs)
            else:
                missing.append(bfbs)

        print(f"  Found {len(found)}/{len(expected_bfbs)} .bfbs files in gen/")
        if missing:
            print(f"  Missing: {', '.join(missing)}")
            print("  FAIL")
            return False
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Error checking .bfbs files: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("=" * 72)
    print("  SMOKE TESTS - Verifying cfxdb installation")
    print("=" * 72)
    print()
    print(f"Python: {sys.version}")
    print()

    tests = [
        ("Test 1", test_import_cfxdb),
        ("Test 2", test_import_zlmdb),
        ("Test 3", test_import_autobahn),
        ("Test 4", test_import_schemas),
        ("Test 5", test_fbs_files),
        ("Test 6", test_bfbs_files),
    ]

    failures = 0
    passed = 0

    for name, test in tests:
        result = test()
        if result is True:
            passed += 1
        else:
            failures += 1
        print()

    total = len(tests)
    print("=" * 72)
    if failures == 0:
        print(f"ALL SMOKE TESTS PASSED ({passed}/{total})")
        print("=" * 72)
        return 0
    else:
        print(f"SMOKE TESTS FAILED ({passed} passed, {failures} failed)")
        print("=" * 72)
        return 1


if __name__ == "__main__":
    sys.exit(main())
