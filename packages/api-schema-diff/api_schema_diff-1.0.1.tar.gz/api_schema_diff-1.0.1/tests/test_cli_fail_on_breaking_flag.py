from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "schema_diff.cli", *args]
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)


def _write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_no_fail_on_breaking_exits_zero(tmp_path: Path):
    old_file = tmp_path / "old.json"
    new_file = tmp_path / "new.json"

    _write_json(old_file, {"User": {"email": "a@b.com", "age": 30}})
    _write_json(new_file, {"User": {"age": 30}})  # breaking: removed email

    proc = _run_cli(
        [str(old_file), str(new_file), "--no-fail-on-breaking"], cwd=tmp_path
    )

    assert proc.returncode == 0, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    assert "BREAKING" in proc.stdout.upper()


def test_fail_on_breaking_default_exits_one(tmp_path: Path):
    old_file = tmp_path / "old.json"
    new_file = tmp_path / "new.json"

    _write_json(old_file, {"User": {"email": "a@b.com", "age": 30}})
    _write_json(new_file, {"User": {"age": 30}})  # breaking

    proc = _run_cli([str(old_file), str(new_file)], cwd=tmp_path)

    assert proc.returncode == 1, f"stdout={proc.stdout}\nstderr={proc.stderr}"


def test_no_fail_on_breaking_json_mode_exits_zero(tmp_path: Path):
    old_file = tmp_path / "old.json"
    new_file = tmp_path / "new.json"

    _write_json(old_file, {"User": {"email": "a@b.com"}})
    _write_json(new_file, {"User": {}})  # breaking

    proc = _run_cli(
        [str(old_file), str(new_file), "--format", "json", "--no-fail-on-breaking"],
        cwd=tmp_path,
    )

    assert proc.returncode == 0, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    # output should still be JSON
    payload = json.loads(proc.stdout)
    assert "breaking" in payload
    assert len(payload["breaking"]) >= 1
