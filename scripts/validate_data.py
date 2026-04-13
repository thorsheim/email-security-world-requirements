#!/usr/bin/env python3
"""
Validate all country YAML files against data/schema/country.schema.json.

Usage:
    python scripts/validate_data.py

Exits with code 0 on success, 1 if any validation errors are found.
Emits warnings for entries with last_reviewed older than 12 months.
"""

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "data" / "schema" / "country.schema.json"
COUNTRIES_DIR = REPO_ROOT / "data" / "countries"
STALE_THRESHOLD_DAYS = 365

STANDARDS_IDS = {"SPF", "DKIM", "DMARC", "DANE", "MTA-STS", "TLS-RPT", "BIMI", "STARTTLS"}


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def validate_country_file(path, schema):
    errors = []
    warnings = []

    try:
        data = load_yaml(path)
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {e}")
        return errors, warnings

    # Schema validation
    validator = jsonschema.Draft7Validator(schema)
    for error in sorted(validator.iter_errors(data), key=str):
        errors.append(f"Schema: {error.json_path} — {error.message}")

    if errors:
        return errors, warnings

    # Filename matches country_code
    expected_code = path.stem.upper()
    actual_code = data.get("country_code", "")
    if actual_code != expected_code and expected_code != "_TEMPLATE":
        errors.append(
            f"country_code '{actual_code}' does not match filename '{path.stem}.yaml'"
        )

    # Staleness check
    last_reviewed_str = data.get("last_reviewed", "")
    if last_reviewed_str:
        try:
            last_reviewed = datetime.strptime(str(last_reviewed_str), "%Y-%m-%d").date()
            age_days = (date.today() - last_reviewed).days
            if age_days > STALE_THRESHOLD_DAYS:
                warnings.append(
                    f"last_reviewed is {age_days} days ago ({last_reviewed_str}) — please re-verify"
                )
        except ValueError:
            warnings.append(f"Could not parse last_reviewed date: '{last_reviewed_str}'")

    # Mandatory/recommended entries must have references
    for req in data.get("requirements", []):
        if req.get("status") in ("mandatory", "recommended"):
            if not req.get("references"):
                warnings.append(
                    f"standard '{req.get('standard')}' has status "
                    f"'{req.get('status')}' but no references"
                )

    return errors, warnings


def main():
    schema = load_schema()
    all_ok = True
    total_countries = 0
    total_warnings = 0

    yaml_files = sorted(COUNTRIES_DIR.glob("*.yaml"))
    # Skip the template file
    yaml_files = [f for f in yaml_files if f.stem != "_template"]

    if not yaml_files:
        print("No country YAML files found in data/countries/")
        sys.exit(1)

    for path in yaml_files:
        total_countries += 1
        errors, warnings = validate_country_file(path, schema)

        if errors:
            all_ok = False
            print(f"\n[FAIL] {path.name}")
            for e in errors:
                print(f"  ERROR: {e}")
        elif warnings:
            print(f"[ OK ] {path.name}")
        else:
            print(f"[ OK ] {path.name}")

        for w in warnings:
            total_warnings += 1
            print(f"  WARN: {w}")

    print(f"\n{total_countries} country files checked.")
    if total_warnings:
        print(f"{total_warnings} warning(s) found.")
    if not all_ok:
        print("Validation FAILED — fix errors above before merging.")
        sys.exit(1)
    else:
        print("All files valid.")


if __name__ == "__main__":
    main()
