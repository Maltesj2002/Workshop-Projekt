#!/usr/bin/env python3
"""
Create a virtual environment with a selected Python interpreter.

Finds all available Python versions, displays them to the user,
and creates a .venv with the selected interpreter (must be >= 3.11).

Works on Windows, macOS, and Linux.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def get_python_version(executable: str) -> Optional[Tuple[int, int, int]]:
    """
    Get the version of a Python executable.
    
    Returns (major, minor, micro) or None if the executable is not Python or fails.
    """
    try:
        result = subprocess.run(
            [executable, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(".")
            return (int(parts[0]), int(parts[1]), int(parts[2]))
    except (FileNotFoundError, ValueError, IndexError, subprocess.TimeoutExpired):
        pass
    return None


def find_python_executables() -> dict[str, Tuple[int, int, int]]:
    """
    Find available Python executables on the system.
    
    Returns a dict mapping executable name to (major, minor, patch) version.
    """
    found = {}
    seen = set()
    
    # Windows: try py launcher first
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["py", "-0p"],
                capture_output=True,
                text=True,
                timeout=3,
            )
        except FileNotFoundError:
            result = None

        if result and result.returncode == 0:
            for line in result.stdout.splitlines():
                # Example: "-3.13-64       C:\\Python313\\python.exe"
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                exe_path = parts[-1]
                if exe_path and exe_path not in seen:
                    version = get_python_version(exe_path)
                    if version:
                        found[exe_path] = version
                        seen.add(exe_path)
    
    # Try common executable names directly first
    base_names = ["python", "python3"]
    for version in ["3.14", "3.13", "3.12", "3.11", "3.10", "3.9"]:
        base_names.append(f"python{version}")
    
    # Try direct calls for cross-platform compatibility
    for candidate in base_names:
        version = get_python_version(candidate)
        if version:
            if candidate not in seen:
                found[candidate] = version
                seen.add(candidate)
    
    # Also try with full paths from which/where if available
    for candidate in base_names:
        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    ["where.exe", candidate],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
            else:
                result = subprocess.run(
                    ["which", candidate],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
            if result.returncode == 0:
                exe_path = result.stdout.strip().split("\n")[0]  # Take first match
                if exe_path and exe_path not in seen:
                    version = get_python_version(exe_path)
                    if version:
                        found[exe_path] = version
                        seen.add(exe_path)
        except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
    
    return found


def format_version(version: Tuple[int, int, int]) -> str:
    """Format a version tuple as a string."""
    return f"{version[0]}.{version[1]}.{version[2]}"


def parse_version_arg(raw: str) -> Tuple[int, int, Optional[int]]:
    """
    Parse a version string like "3.12" or "3.12.10".

    Returns (major, minor, micro_or_none).
    """
    parts = raw.strip().split(".")
    if len(parts) not in (2, 3):
        raise ValueError("Version must be in MAJOR.MINOR or MAJOR.MINOR.MICRO format.")
    major = int(parts[0])
    minor = int(parts[1])
    micro = int(parts[2]) if len(parts) == 3 else None
    return major, minor, micro


def select_by_version(
    candidates: list[tuple[str, Tuple[int, int, int]]],
    version_arg: str,
) -> Optional[tuple[str, Tuple[int, int, int]]]:
    """Select a matching interpreter based on a version argument."""
    major, minor, micro = parse_version_arg(version_arg)
    if micro is None:
        matching = [item for item in candidates if item[1][0] == major and item[1][1] == minor]
    else:
        matching = [item for item in candidates if item[1] == (major, minor, micro)]
    if not matching:
        return None
    return max(matching, key=lambda item: item[1])


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a virtual environment with a selected Python interpreter.",
    )
    parser.add_argument(
        "--version",
        help="Pin the interpreter version (e.g., 3.12 or 3.12.10).",
    )
    args = parser.parse_args()

    print("Searching for Python interpreters...\n")
    
    # Find all Python executables
    found = find_python_executables()
    
    if not found:
        print("Error: No Python interpreters found on your system.")
        print("Please install Python 3.11+ and try again.")
        return 1
    
    # Filter and sort by version (descending)
    valid = {exe: ver for exe, ver in found.items() if ver >= (3, 11)}
    
    if not valid:
        print("Available Python versions:")
        for exe, ver in sorted(found.items(), key=lambda x: x[1], reverse=True):
            print(f"  {exe}: {format_version(ver)}")
        print("\nError: No Python >= 3.11 found.")
        print("Install Python 3.11+ (3.11–3.13 recommended) and try again.")
        return 1
    
    # Sort by version descending (prefer newer versions)
    sorted_executables = sorted(valid.items(), key=lambda x: x[1], reverse=True)

    if args.version:
        try:
            selected = select_by_version(sorted_executables, args.version)
        except ValueError as exc:
            print(f"Error: {exc}")
            return 1

        if not selected:
            print("Available Python versions (>= 3.11):")
            for exe, ver in sorted_executables:
                print(f"  {exe}: {format_version(ver)}")
            print(f"\nError: No Python matching {args.version} found.")
            return 1

        selected_exe, selected_ver = selected
    else:
        print("Available Python versions (>= 3.11):")
        for i, (exe, ver) in enumerate(sorted_executables, 1):
            print(f"  [{i}] {exe}: {format_version(ver)}")
    
        # Prompt user
        print()
        while True:
            try:
                choice = input(
                    f"Select Python version [1-{len(sorted_executables)}] (default: 1): "
                ).strip()
                if not choice:
                    choice = "1"
                idx = int(choice) - 1
                if 0 <= idx < len(sorted_executables):
                    selected_exe, selected_ver = sorted_executables[idx]
                    break
                print(f"Please enter a number between 1 and {len(sorted_executables)}.")
            except ValueError:
                print(f"Please enter a valid number between 1 and {len(sorted_executables)}.")
    
    # Create venv
    venv_path = Path(".venv")
    print(f"\nCreating virtual environment with {selected_exe} ({format_version(selected_ver)})...")
    
    try:
        result = subprocess.run(
            [selected_exe, "-m", "venv", str(venv_path)],
            check=False,
        )
        if result.returncode != 0:
            print("Error: Failed to create virtual environment.")
            return 1
    except FileNotFoundError:
        print(f"Error: Could not find {selected_exe}")
        return 1
    
    # Print next steps
    print(f"\n✓ Virtual environment created at {venv_path}")
    print("\nNext steps:")
    if sys.platform == "win32":
        venv_python = f".\\{venv_path}\\Scripts\\python.exe"
        print(f"  1. Activate (optional):  .\\{venv_path}\\Scripts\\Activate.ps1")
        print(f"  2. Upgrade pip: {venv_python} -m pip install -U pip")
        print(f"  3. Install dependencies: {venv_python} -m pip install -e \".[dev,notebooks]\"")
    else:
        venv_python = f"{venv_path}/bin/python"
        print(f"  1. Activate (optional):  source {venv_path}/bin/activate")
        print(f"  2. Upgrade pip: {venv_python} -m pip install -U pip")
        print(f"  3. Install dependencies: {venv_python} -m pip install -e \".[dev,notebooks]\"")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
