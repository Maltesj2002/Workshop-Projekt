import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


def _load_create_venv_module():
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "create_venv.py"

    spec = importlib.util.spec_from_file_location("create_venv_script", script_path)
    assert spec and spec.loader

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_find_python_executables_windows_no_py_launcher_does_not_crash(monkeypatch):
    mod = _load_create_venv_module()

    # Force the Windows code path regardless of the OS running the tests.
    monkeypatch.setattr(mod.sys, "platform", "win32")

    def fake_run(args, **kwargs):
        if args[:2] == ["py", "-0p"]:
            raise FileNotFoundError("py launcher not found")
        return SimpleNamespace(returncode=1, stdout="")

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    monkeypatch.setattr(mod, "get_python_version", lambda exe: None)

    found = mod.find_python_executables()
    assert isinstance(found, dict)


def test_find_python_executables_uses_py_0p_paths(monkeypatch):
    mod = _load_create_venv_module()

    monkeypatch.setattr(mod.sys, "platform", "win32")

    def fake_run(args, **kwargs):
        if args[:2] == ["py", "-0p"]:
            return SimpleNamespace(
                returncode=0,
                stdout=(
                    "-3.12-64 C:\\Python312\\python.exe\n"
                    "-3.11-64 C:\\Python311\\python.exe\n"
                ),
            )
        # Avoid picking up anything via where.exe during this test.
        return SimpleNamespace(returncode=1, stdout="")

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    def fake_get_python_version(exe: str):
        if exe.endswith("Python312\\python.exe"):
            return (3, 12, 0)
        if exe.endswith("Python311\\python.exe"):
            return (3, 11, 9)
        return None

    monkeypatch.setattr(mod, "get_python_version", fake_get_python_version)

    found = mod.find_python_executables()
    assert found["C:\\Python312\\python.exe"] == (3, 12, 0)
    assert found["C:\\Python311\\python.exe"] == (3, 11, 9)
