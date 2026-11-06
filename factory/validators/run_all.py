"""Run all factory validators. Exit code 1 if any error. Used by `make validate`."""
import sys

import honest_claims
import schemas_and_adrs
import skill_structure
from common import REPO_ROOT


def main() -> int:
    findings = skill_structure.validate_all(REPO_ROOT) + honest_claims.scan_repo(REPO_ROOT)
    findings += schemas_and_adrs.validate_schemas(REPO_ROOT) + schemas_and_adrs.validate_adrs(REPO_ROOT)
    for f in findings:
        print(f)
    errors = [f for f in findings if f.severity == "error"]
    print(f"validators: {len(errors)} error(s), {len(findings) - len(errors)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
