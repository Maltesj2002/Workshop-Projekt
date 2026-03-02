#!/usr/bin/env python
"""Validate code structure to enforce document-driven development principles.

Checks:
- No monolithic notebooks (>300 cells or >3000 lines per notebook)
- No folium/matplotlib/plotly imports
- No !pip install in notebooks
- All dependencies in pyproject.toml
"""
import json
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent

ERRORS = []
WARNINGS = []

def check_notebook_structure():
    """Check notebooks aren't monolithic."""
    notebooks = list(WORKSPACE.glob("notebooks/**/*.ipynb"))
    
    for nb_file in notebooks:
        try:
            with open(nb_file) as f:
                nb = json.load(f)
            
            num_cells = len(nb.get("cells", []))
            total_lines = sum(
                len(cell.get("source", [])) 
                for cell in nb.get("cells", [])
            )
            
            if num_cells > 300:
                ERRORS.append(
                    f"⚠️  {nb_file.relative_to(WORKSPACE)} has {num_cells} cells (max 300). "
                    f"Split into separate agent notebooks."
                )
            
            if total_lines > 3000:
                ERRORS.append(
                    f"⚠️  {nb_file.relative_to(WORKSPACE)} has {total_lines} lines (max 3000). "
                    f"This looks monolithic. Split it into agent notebooks."
                )
            
            # Check for forbidden imports
            for cell in nb.get("cells", []):
                if cell.get("cell_type") == "code":
                    source = "".join(cell.get("source", []))
                    
                    if re.search(r"import folium|from folium", source):
                        ERRORS.append(
                            f"❌ {nb_file.relative_to(WORKSPACE)}: Uses folium. "
                            f"Use anymap-ts instead (see .github/copilot-instructions.md)."
                        )
                    
                    if re.search(r"import matplotlib|from matplotlib", source):
                        WARNINGS.append(
                            f"⚠️  {nb_file.relative_to(WORKSPACE)}: Uses matplotlib. "
                            f"OK for static plots but use anymap-ts for real-time maps."
                        )
                    
                    if re.search(r"import plotly|from plotly", source):
                        WARNINGS.append(
                            f"⚠️  {nb_file.relative_to(WORKSPACE)}: Uses plotly. "
                            f"OK for static dashboards but use anymap-ts for real-time MQTT data."
                        )
                    
                    if re.search(r"!pip install", source):
                        ERRORS.append(
                            f"❌ {nb_file.relative_to(WORKSPACE)}: Uses !pip install. "
                            f"Add to pyproject.toml instead, then run `pip install -e '.[notebooks]'`."
                        )
                    
                    if re.search(r'subprocess\.run\(\["pip"', source):
                        ERRORS.append(
                            f"❌ {nb_file.relative_to(WORKSPACE)}: Uses subprocess to install packages. "
                            f"Add dependencies to pyproject.toml."
                        )
        
        except json.JSONDecodeError:
            ERRORS.append(f"❌ {nb_file.relative_to(WORKSPACE)}: Invalid notebook JSON")

def check_pyproject():
    """Check pyproject.toml has proper dependencies."""
    pyproject = WORKSPACE / "pyproject.toml"
    if not pyproject.exists():
        return
    
    content = pyproject.read_text()
    
    if "anymap-ts" not in content:
        WARNINGS.append(
            "⚠️  pyproject.toml: anymap-ts not in optional dependencies. "
            "Add it to [project.optional-dependencies] notebooks section."
        )
    
    if "folium" in content:
        ERRORS.append(
            "❌ pyproject.toml: folium is explicitly listed. Remove it. Use anymap-ts instead."
        )

def check_notebooks_mqtt():
    """Warn if notebooks don't use mqtt helpers."""
    notebooks = list(WORKSPACE.glob("notebooks/**/*.ipynb"))
    
    for nb_file in notebooks:
        # Skip dashboard files (they may not publish)
        if "dashboard" in nb_file.name or "viz" in nb_file.name:
            continue
        
        try:
            with open(nb_file) as f:
                nb = json.load(f)
            
            source = "".join(
                "".join(cell.get("source", []))
                for cell in nb.get("cells", [])
                if cell.get("cell_type") == "code"
            )
            
            # Agent notebooks should use mqtt
            if "agent" in nb_file.name:
                if "mqtt.connect_mqtt" not in source:
                    WARNINGS.append(
                        f"⚠️  {nb_file.relative_to(WORKSPACE)}: Agent notebook but no mqtt.connect_mqtt(). "
                        f"Does it need to publish/subscribe?"
                    )
        
        except json.JSONDecodeError:
            pass

def main():
    print("\n🔍 Checking code structure for document-driven development compliance...\n")
    
    check_notebook_structure()
    check_pyproject()
    check_notebooks_mqtt()
    
    if ERRORS:
        print("❌ ERRORS (must fix):")
        for err in ERRORS:
            print(f"  {err}")
        print()
    
    if WARNINGS:
        print("⚠️  WARNINGS (consider fixing):")
        for warn in WARNINGS:
            print(f"  {warn}")
        print()
    
    if not ERRORS and not WARNINGS:
        print("✅ All checks passed!\n")
        return 0
    
    if ERRORS:
        print("=" * 70)
        print("❌ Fix these errors before submitting.")
        print("=" * 70 + "\n")
        return 1
    else:
        print("=" * 70)
        print("⚠️  Warnings found, but no blocking errors.")
        print("=" * 70 + "\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())
