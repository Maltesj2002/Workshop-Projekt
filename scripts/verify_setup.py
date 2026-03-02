#!/usr/bin/env python
"""Verify that the environment is set up correctly for the workshop."""
import sys
import importlib.util

REQUIRED_PACKAGES = {
    "paho": "paho-mqtt",
    "yaml": "PyYAML",
    "dotenv": "python-dotenv",
}

NOTEBOOK_PACKAGES = {
    "jupyterlab": "jupyterlab",
    "anymap_ts": "anymap-ts (geospatial mapping)",
}

FORBIDDEN_PACKAGES = {
    "folium": "folium (conflicts with anymap-ts workflow)",
    "folium_map": "folium_map",
}

def check_package(module_name: str, package_display: str) -> bool:
    """Check if a package is installed."""
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        print(f"✅ {package_display}")
        return True
    else:
        print(f"❌ {package_display} (missing)")
        return False

def main():
    print("\n🔍 Verifying workshop environment...\n")
    
    all_ok = True
    
    # Check required packages
    print("Required packages:")
    for module, display in REQUIRED_PACKAGES.items():
        if not check_package(module, display):
            all_ok = False
    
    # Check notebook packages
    print("\nNotebook packages:")
    in_notebook_env = True
    for module, display in NOTEBOOK_PACKAGES.items():
        if not check_package(module, display):
            all_ok = False
            in_notebook_env = False
    
    # Check for forbidden packages
    print("\nChecking for conflicting packages:")
    for module, display in FORBIDDEN_PACKAGES.items():
        spec = importlib.util.find_spec(module)
        if spec is not None:
            print(f"⚠️  {display} (installed - remove it)")
            all_ok = False
        else:
            print(f"✅ {display} (not installed)")
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ Environment is set up correctly!")
    elif in_notebook_env:
        print("❌ Some packages are missing or conflicting.")
        print("\nRun this to fix:")
        print("  pip install -e '.[dev,notebooks]'")
    else:
        print("❌ Missing notebook packages.")
        print("\nRun this to set up notebooks:")
        print("  pip install -e '.[notebooks]'")
    print("=" * 60 + "\n")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
