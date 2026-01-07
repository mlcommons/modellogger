import pathlib
import re
import subprocess
import sys
from datetime import datetime, timedelta, UTC

from tests import example_cli


def run_cli(*args) -> subprocess.CompletedProcess:
    # noinspection PyTypeChecker
    target = pathlib.Path(example_cli.__file__).parent / "example_cli.py"
    result = subprocess.run([sys.executable, str(target)] + list(args), capture_output=True)
    return result


def test_basics():
    r = run_cli()
    assert r.returncode == 0
    assert r.stdout.decode() == "Hello World\n"
    log_lines = parse_log_lines(r)
    print(len(log_lines))

    for l in log_lines:
        # print(l)
        assert datetime.now(tz=UTC) - datetime.fromisoformat(l['datetime']) < timedelta(seconds=1)
        assert l['app'] == "example_cli"
    assert len(log_lines) == 3

    assert log_lines[0]['name'] == "__main__"
    assert log_lines[0]['level'] == "INFO"
    assert log_lines[0]['message'] == "info in cli"

    assert log_lines[1]['name'] == "tests.example_top_library"
    assert log_lines[1]['level'] == "INFO"
    assert log_lines[1]['message'] == "info in tests.example_top_library"

    assert log_lines[2]['name'] == "tests.example_lower_library"
    assert log_lines[2]['level'] == "INFO"
    assert log_lines[2]['message'] == "info in tests.example_lower_library"


# example: '\x1b[97m2026-01-07T17:47:46Z - example_cli - tests.example_cli - INFO - cli info\x1b[0m'
LOG_PATTERN = r".*(?P<datetime>[0-9]{4}-.*?) - (?P<app>.+?) - (?P<name>.+?) - (?P<level>\w+) - (?P<message>.+?)(\x1b.*|$)"


def parse_log_lines(r: subprocess.CompletedProcess) -> list[dict[str, str]]:
    log_lines = r.stderr.decode().strip().split("\n")
    result = []
    for l in log_lines:
        if not l:
            continue
        m = re.match(LOG_PATTERN, l)
        if m:
            result.append(m.groupdict())
        else:
            print("couldn't parse: " + l, sys.stderr)
    return result
