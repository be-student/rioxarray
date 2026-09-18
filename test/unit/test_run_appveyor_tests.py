from pathlib import Path

import pytest

from test.run_appveyor_tests import junit_succeeded, verified_windows_teardown_failure


@pytest.mark.parametrize(
    ("attributes", "expected"),
    [
        ({"tests": "10", "errors": "0", "failures": "0"}, True),
        ({"tests": "10", "errors": "1", "failures": "0"}, False),
        ({"tests": "10", "errors": "0", "failures": "1"}, False),
        ({"tests": "0", "errors": "0", "failures": "0"}, False),
    ],
)
def test_junit_succeeded(tmp_path: Path, attributes: dict[str, str], expected: bool):
    report_path = tmp_path / "report.xml"
    xml_attributes = " ".join(f'{key}="{value}"' for key, value in attributes.items())
    report_path.write_text(
        f"<testsuites><testsuite {xml_attributes}/></testsuites>", encoding="utf-8"
    )
    assert junit_succeeded(report_path) is expected


def test_junit_succeeded_rejects_invalid_report(tmp_path: Path):
    report_path = tmp_path / "report.xml"
    report_path.write_text("not XML", encoding="utf-8")
    assert not junit_succeeded(report_path)


@pytest.mark.parametrize("returncode", [-1073741819, 3221225477])
def test_verified_windows_teardown_failure(tmp_path: Path, returncode: int):
    report_path = tmp_path / "report.xml"
    report_path.write_text(
        '<testsuite tests="10" errors="0" failures="0"/>', encoding="utf-8"
    )
    assert verified_windows_teardown_failure(returncode, "win32", report_path)
    assert not verified_windows_teardown_failure(returncode, "darwin", report_path)
    assert not verified_windows_teardown_failure(1, "win32", report_path)
