import json
import subprocess
import sys
from pathlib import Path


def _run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """
    Run the CLI as a module to avoid depending on installed console scripts.
    """
    cmd = [sys.executable, "-m", "schema_diff.cli", *args]
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
    )


def _write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_cli_exit_code_0_when_no_breaking(tmp_path: Path):
    old_file = tmp_path / "old.json"
    new_file = tmp_path / "new.json"

    _write_json(old_file, {"User": {"age": 30}})
    _write_json(new_file, {"User": {"age": 30}})

    proc = _run_cli([str(old_file), str(new_file)], cwd=tmp_path)

    assert proc.returncode == 0, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    # stderr should be empty on success (Typer/Rich generally prints to stdout)
    assert proc.stderr.strip() == ""


def test_cli_exit_code_1_when_breaking(tmp_path: Path):
    old_file = tmp_path / "old.json"
    new_file = tmp_path / "new.json"

    _write_json(old_file, {"User": {"email": "a@b.com", "age": 30}})
    _write_json(new_file, {"User": {"age": 30}})  # removed email => breaking

    proc = _run_cli([str(old_file), str(new_file)], cwd=tmp_path)

    assert proc.returncode == 1, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    assert "BREAKING" in proc.stdout.upper()
    assert proc.stderr.strip() == ""


def test_cli_json_output_is_valid_and_contains_expected_changes(tmp_path: Path):
    old_file = tmp_path / "old.json"
    new_file = tmp_path / "new.json"

    _write_json(
        old_file, {"User": {"email": "a@b.com", "age": 30}, "Order": {"amount": 12.5}}
    )
    _write_json(
        new_file, {"User": {"age": 30}, "Order": {"amount": "12.5"}}
    )  # removed email + type change

    proc = _run_cli([str(old_file), str(new_file), "--format", "json"], cwd=tmp_path)

    assert proc.returncode == 1, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    assert proc.stderr.strip() == ""

    # Rich prints JSON to stdout; when not a TTY it should be parseable JSON.
    payload = json.loads(proc.stdout)

    assert "breaking" in payload
    assert "non_breaking" in payload

    breaking = payload["breaking"]
    assert isinstance(breaking, list)

    # Expect at least these two breaking changes:
    # - removed_field at User.email
    # - type_change at Order.amount
    breaking_types_paths = {(c["type"], c["path"]) for c in breaking}

    assert ("removed_field", "User.email") in breaking_types_paths
    assert ("type_change", "Order.amount") in breaking_types_paths
