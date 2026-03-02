# Setup

This project targets **Python 3.11+**.

In practice, the smoothest experience is usually with Python **3.11–3.13**. Newer versions (for example Python 3.14 right after release) may work, but some third-party packages may not have prebuilt wheels available yet, which can cause installs (for example `python -m pip install ...`) to fail.

The package metadata enforces this (`requires-python >= 3.11`), so installs will fail on older Python versions.

## Create and activate a virtual environment

If you have multiple Python versions installed, you may accidentally create the virtual environment with an older interpreter (for example Python 3.9/3.10). The interpreter you use to run `-m venv` is the Python version that will be used inside `.venv`.

### All platforms (recommended)

Use the Python helper script. It finds all Python versions on your system, lists them, and prompts you to choose one.

```bash
python3 scripts/create_venv.py
```

### Manual setup ( after the script )

macOS / Linux:

```bash
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev, geo, notebooks]"
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev, geo, notebooks]"
```

### when returning to the project

If VS- code does not automaticly open the .venv in the terminal thye

macOS / Linux:

```bash
source .venv/bin/activate

```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

If the script does not list a Python version that is >= 3.11, install it first:

- macOS (Homebrew):

```bash
brew install python@3.12
```

- Windows: download and run the installer from [https://www.python.org/downloads/](https://www.python.org/downloads/)

If you already created `.venv` with the wrong Python version, delete `.venv` and create it again with the correct interpreter.

### Verify your installation

After installing, verify that all packages are correct:

```bash
python scripts/verify_setup.py
```

This checks that you have:

- Required packages (paho-mqtt, PyYAML, python-dotenv)
- Notebook tools (`jupyterlab`, `anymap-ts`)
- No conflicting packages (e.g., `folium`)

If the check fails, run the install command above again.

## Optional: geospatial transforms (CRS)

If you plan to work with real-world coordinates, install the optional geospatial
extra to enable EPSG transforms.

Geo helpers live in `simulated_city.geo` and include convenience functions like
`wgs2utm(...)` / `utm2wgs(...)` plus the general `transform_xy(...)`.

```bash
python -m pip install -e ".[geo]"
```

Tip: for notebooks that include both mapping + CRS transforms, you can install both extras:

```bash
python -m pip install -e ".[notebooks,geo]"
```

## Set up a local MQTT broker (optional)

If you want to test MQTT locally before connecting to a public broker, install **Mosquitto**:

### macOS (using Homebrew)

```bash
brew install mosquitto
brew services start mosquitto
```

Verify it's running:

```bash
lsof -i :1883
```

You should see `mosquitto` listening on port 1883.

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install mosquitto
sudo systemctl start mosquitto
```

### Windows

Download the installer from [mosquitto.org](https://mosquitto.org/download/) or use Windows Subsystem for Linux (WSL).

## Troubleshooting

### I installed `folium` or another mapping library

Remove it immediately:

```bash
python -m pip uninstall folium folium-map
```

The workshop uses **`anymap-ts`** as the mapping tool. It integrates better with real-time MQTT data streams and geospatial transforms. Other tools (like `folium`, `matplotlib`, `plotly`) are not compatible with this workshop's structure.

### I see "ModuleNotFoundError: No module named 'anymap_ts'"

Run the verification script:

```bash
python scripts/verify_setup.py
```

Then reinstall with the correct extras:

```bash
python -m pip install -e ".[notebooks]"
```

### Notebooks are in one big file instead of communicating via MQTT

This is a common mistake. You should structure notebooks as independent agents that publish/subscribe via MQTT:

- `notebooks/agent_transport.ipynb` — simulates transport, publishes traffic data
- `notebooks/agent_environment.ipynb` — simulates air quality, subscribes to traffic data
- `notebooks/dashboard.ipynb` — subscribes to all agent topics, visualizes with `anymap-ts`

See [exercises.md](exercises.md) for examples.

## Run tests

Run tests to verify the libraries are installed, especially MQTT broker support. The MQTT tests validate all configured MQTT profiles (see `config.yaml`) and confirm the MQTT password is set in `.env`.

```bash
python -m pytest
```

## Run notebooks

By default, run notebooks in VS Code: open a notebook in `notebooks/` and select the `.venv` kernel.

You can also run notebooks in a browser by starting JupyterLab:

```bash
python -m jupyterlab
```
