#!/usr/bin/env python3
# Copyright (c) typedef int GmbH, Germany, 2025. All rights reserved.
#
# Smoke tests for xbr package verification.
# Used by CI to verify wheels and sdists actually work after building.

"""
Smoke tests for xbr package.

This script verifies that an xbr installation is functional by testing:
1. Import xbr and check version
2. Import xbr ABI files (critical - this is what v25.12.1 broke!)
3. Import core XBR types (EIP712, FbsObject, etc.)
4. Import dependencies (autobahn, zlmdb, web3)
5. Verify contract source files are bundled
6. Verify template files are bundled

ALL TESTS ARE REQUIRED. Both wheel installs and sdist installs MUST
provide identical functionality.
"""

import sys
from pathlib import Path


def test_import_xbr():
    """Test 1: Import xbr and check version."""
    print("Test 1: Importing xbr and checking version...")
    try:
        import xbr
        print(f"  xbr version: {xbr.__version__}")
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import xbr: {e}")
        return False


def test_import_abi():
    """Test 2: Import xbr ABI files (critical test!)."""
    print("Test 2: Verifying ABI files are accessible...")
    try:
        from xbr._abi import (
            XBR_TOKEN_FN,
            XBR_NETWORK_FN,
            XBR_MARKET_FN,
            XBR_CHANNEL_FN,
            XBR_CATALOG_FN,
        )

        # Check each ABI file exists
        abi_files = {
            "XBRToken.json": XBR_TOKEN_FN,
            "XBRNetwork.json": XBR_NETWORK_FN,
            "XBRMarket.json": XBR_MARKET_FN,
            "XBRChannel.json": XBR_CHANNEL_FN,
            "XBRCatalog.json": XBR_CATALOG_FN,
        }

        found = []
        missing = []
        for name, path in abi_files.items():
            if Path(path).exists():
                found.append(name)
                print(f"    {name}: OK")
            else:
                missing.append(name)
                print(f"    {name}: MISSING at {path}")

        if missing:
            print(f"  FAIL: Missing ABI files: {', '.join(missing)}")
            return False

        print(f"  Found {len(found)}/{len(abi_files)} ABI files")
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import xbr._abi: {e}")
        return False


def test_import_core_types():
    """Test 3: Import core XBR types."""
    print("Test 3: Importing core XBR types...")
    try:
        from xbr import FbsObject
        print("  FbsObject: OK")

        from xbr import EIP712AuthorityCertificate
        print("  EIP712AuthorityCertificate: OK")

        from xbr import EIP712DelegateCertificate
        print("  EIP712DelegateCertificate: OK")

        from xbr import parse_certificate_chain
        print("  parse_certificate_chain: OK")

        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import core types: {e}")
        return False


def test_import_dependencies():
    """Test 4: Import xbr dependencies."""
    print("Test 4: Importing xbr dependencies...")
    try:
        import autobahn
        print(f"  autobahn version: {autobahn.__version__}")

        import zlmdb
        print(f"  zlmdb version: {zlmdb.__version__}")

        from zlmdb import flatbuffers
        print("  zlmdb.flatbuffers: available")

        from web3 import Web3
        print("  web3: available")

        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Could not import dependencies: {e}")
        return False


def test_contract_files():
    """Test 5: Verify Solidity contract source files are bundled."""
    print("Test 5: Verifying contract source files are bundled...")
    try:
        import xbr
        xbr_path = Path(xbr.__file__).parent
        contract_path = xbr_path / "contract"

        # Expected contract files
        expected_contracts = [
            "XBRToken.sol",
            "XBRNetwork.sol",
            "XBRMarket.sol",
            "XBRChannel.sol",
            "XBRCatalog.sol",
        ]

        found = []
        missing = []
        for contract in expected_contracts:
            sol_path = contract_path / contract
            if sol_path.exists():
                found.append(contract)
            else:
                missing.append(contract)

        print(f"  Found {len(found)}/{len(expected_contracts)} contract files")
        if missing:
            print(f"  Missing: {', '.join(missing)}")
            print("  FAIL")
            return False
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Error checking contract files: {e}")
        return False


def test_template_files():
    """Test 6: Verify template files are bundled."""
    print("Test 6: Verifying template files are bundled...")
    try:
        import xbr
        xbr_path = Path(xbr.__file__).parent
        template_path = xbr_path / "templates" / "py-autobahn"

        # Expected template files
        expected_templates = [
            "obj.py.jinja2",
            "service.py.jinja2",
            "enum.py.jinja2",
        ]

        found = []
        missing = []
        for template in expected_templates:
            tpl_path = template_path / template
            if tpl_path.exists():
                found.append(template)
            else:
                missing.append(template)

        print(f"  Found {len(found)}/{len(expected_templates)} template files")
        if missing:
            print(f"  Missing: {', '.join(missing)}")
            print("  FAIL")
            return False
        print("  PASS")
        return True
    except Exception as e:
        print(f"  FAIL: Error checking template files: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("=" * 72)
    print("  SMOKE TESTS - Verifying xbr installation")
    print("=" * 72)
    print()
    print(f"Python: {sys.version}")
    print()

    tests = [
        ("Test 1", test_import_xbr),
        ("Test 2", test_import_abi),
        ("Test 3", test_import_core_types),
        ("Test 4", test_import_dependencies),
        ("Test 5", test_contract_files),
        ("Test 6", test_template_files),
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
