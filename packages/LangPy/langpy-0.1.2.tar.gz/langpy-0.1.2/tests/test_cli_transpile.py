import sys
import subprocess
from pathlib import Path


def run_langpy(*args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "langpy", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_transpile_single_file(tmp_path):
    src = tmp_path / "main.pyes"
    src.write_text("imprimir('hola')", encoding="utf-8")

    result = run_langpy("--transpile", "main.pyes", cwd=tmp_path)
    assert result.returncode == 0

    out = tmp_path / "main.py"
    assert out.exists()
    assert "print" in out.read_text(encoding="utf-8")


def test_transpile_does_not_execute(tmp_path):
    src = tmp_path / "main.pyes"
    src.write_text("imprimir('NO EJECUTAR')", encoding="utf-8")

    result = run_langpy("--transpile", "main.pyes", cwd=tmp_path)
    assert "NO EJECUTAR" not in result.stdout
