"""Run pytest and verify results before tolerating a native teardown crash."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

WINDOWS_ACCESS_VIOLATION = {-1073741819, 3221225477}


def junit_succeeded(report_path: Path) -> bool:
    """Return whether a complete JUnit report contains only passing tests."""
    try:
        root = ET.parse(report_path).getroot()
    except (ET.ParseError, OSError):
        return False
    test_suites = [root] if root.tag == "testsuite" else root.findall(".//testsuite")
    if not test_suites:
        return False
    tests = sum(int(test_suite.get("tests", 0)) for test_suite in test_suites)
    errors = sum(int(test_suite.get("errors", 0)) for test_suite in test_suites)
    failures = sum(int(test_suite.get("failures", 0)) for test_suite in test_suites)
    return tests > 0 and errors == 0 and failures == 0


def verified_windows_teardown_failure(
    returncode: int, platform: str, report_path: Path
) -> bool:
    """Return whether Windows crashed only after pytest reported success."""
    return (
        platform == "win32"
        and returncode in WINDOWS_ACCESS_VIOLATION
        and junit_succeeded(report_path)
    )


def main(pytest_args: list[str]) -> int:
    """Run pytest and validate its report before accepting a teardown crash."""
    report_path = Path(tempfile.gettempdir()) / "rioxarray-appveyor-results.xml"
    report_path.unlink(missing_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            f"--junitxml={report_path}",
            *pytest_args,
        ],
        check=False,
    )
    if result.returncode == 0:
        return 0
    if verified_windows_teardown_failure(
        result.returncode, sys.platform, report_path
    ):
        print(
            "pytest completed successfully before Windows native teardown "
            f"exited with {result.returncode}; accepting the verified JUnit report."
        )
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
