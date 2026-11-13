"""Validate every data contract in contracts/ before it can be merged.

Checks structure only (required keys, column fields, allowed types, one primary key).
Run: python scripts/validate_contracts.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED_KEYS = {"contract_version", "table", "description", "owner", "classification", "schema"}
ALLOWED_TYPES = {"string", "int", "bigint", "double", "decimal", "boolean", "date", "timestamp"}
ALLOWED_CLASSIFICATIONS = {"public", "internal", "confidential", "restricted"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    contract = yaml.safe_load(path.read_text()) or {}

    missing = REQUIRED_KEYS - contract.keys()
    if missing:
        errors.append(f"missing keys: {sorted(missing)}")

    if contract.get("classification") not in ALLOWED_CLASSIFICATIONS:
        errors.append(f"classification must be one of {sorted(ALLOWED_CLASSIFICATIONS)}")

    if str(contract.get("table", "")).count(".") != 2:
        errors.append("table must be a three-level Unity Catalog name: catalog.schema.table")

    columns = contract.get("schema") or []
    names = [c.get("name") for c in columns]
    if len(names) != len(set(names)):
        errors.append("duplicate column names")
    for col in columns:
        if col.get("type") not in ALLOWED_TYPES:
            errors.append(f"column {col.get('name')!r}: unsupported type {col.get('type')!r}")
        if "nullable" not in col:
            errors.append(f"column {col.get('name')!r}: 'nullable' must be stated")
    if sum(1 for c in columns if c.get("primary_key")) != 1:
        errors.append("exactly one column must be marked primary_key")

    return errors


def main() -> int:
    contracts = sorted(Path("contracts").glob("*.yaml"))
    if not contracts:
        print("no contracts found")
        return 1
    failed = False
    for path in contracts:
        errors = validate(path)
        status = "OK" if not errors else "FAIL"
        print(f"[{status}] {path}")
        for err in errors:
            print(f"    - {err}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
