# Testing Guide

This document describes the test suite for the Simulated City template, including how to run tests and what each test module validates.

## Overview

The test suite uses **pytest** and covers four main areas:
- Configuration loading (single and multi-broker support)
- Geospatial coordinate transforms
- MapLibre map integration
- MQTT connectivity and publishing

All tests pass with a local Mosquitto broker running on `localhost:1883`.

## Running Tests

### Run all tests

```bash
python -m pytest tests/ -v
```

### Run a specific test module

```bash
# Configuration tests
python -m pytest tests/test_config.py -v

# MQTT connectivity tests
python -m pytest tests/test_smoke.py -v

# Coordinate transform tests
python -m pytest tests/test_geo.py -v

# MapLibre integration tests
python -m pytest tests/test_maplibre_live.py -v
```

### Run a specific test function

```bash
python -m pytest tests/test_config.py::test_load_config_multi_broker_with_active_profiles -v
```

## Test Modules

### test_config.py

Configuration loading and validation with support for single and multi-broker setups.

| Test | Purpose |
|------|---------|
| `test_load_config_defaults_when_missing()` | Verify sensible defaults (localhost:1883) when config file is missing |
| `test_load_config_reads_yaml()` | Parse YAML config with multi-broker profile structure |
| `test_load_config_finds_parent_config_yaml()` | Discover config in parent directories (useful for running notebooks/ from root) |
| `test_load_config_multi_broker_with_active_profiles()` | Load multiple brokers via `active_profiles` list and verify primary broker selection |
| `test_load_config_single_broker_with_active_profiles()` | Single-broker configuration remains backward compatible |

**Key Validations:**
- Primary broker is the first profile in `active_profiles` list
- All brokers accessible by name via `cfg.mqtt_configs` dictionary
- Config inheritance: common settings override by profile-specific settings
- Default profile handling when no explicit configuration exists

### test_smoke.py

MQTT connectivity tests with multi-broker support. Tests skip automatically if Mosquitto is not running.

| Test | Purpose |
|------|---------|
| `test_mqtt_connection_and_publish()` | Connect to primary broker and publish a JSON test message |
| `test_multi_broker_config_available()` | Verify multi-broker configuration is correctly loaded and accessible |
| `test_mqtt_connection_via_broker_name()` | Connect to a specific broker by name from `mqtt_configs` dictionary |

**Prerequisites:**
- Mosquitto broker running on localhost:1883
- Tests automatically skip if broker is unavailable

**Key Validations:**
- Primary broker (`cfg.mqtt`) successfully connects
- All brokers in `mqtt_configs` dictionary have correct connection details
- Primary broker is the first profile in the active profiles list
- Connection cleanup works (client disconnects properly)

### test_geo.py

Geospatial coordinate transformation tests.

| Test | Purpose |
|------|---------|
| `test_wgs2utm_transforms_coordinates()` | Convert WGS84 coordinates to UTM (EPSG:25832) |
| `test_utm2wgs_transforms_coordinates()` | Convert UTM coordinates back to WGS84 |

**Key Validations:**
- Coordinate transforms are mathematically accurate
- Round-trip WGS84 ↔ UTM conversion is reversible
- CRS definitions are correct (EPSG codes)

### test_maplibre_live.py

MapLibre map integration tests.

| Test | Purpose |
|------|---------|
| `test_create_anymap_viewer()` | Create an Anymap viewer instance |
| `test_anymap_viewer_has_expected_methods()` | Verify required methods exist on viewer |
| `test_set_zoom_and_center()` | Set map zoom and center coordinates |

**Key Validations:**
- MapLibre integration is initialized correctly
- Viewer API methods are available
- Map properties (zoom, center) can be set

## Multi-Broker Configuration Testing

The test suite validates the multi-broker architecture introduced in this template:

```yaml
mqtt:
  active_profiles: [local, public]
  profiles:
    local:
      host: localhost
      port: 1883
    public:
      host: broker.example.com
      port: 1883
```

**What's tested:**

1. **Configuration Loading**: Multiple profiles load correctly via `active_profiles` list
2. **Primary Broker Selection**: First profile in list becomes the primary broker (`cfg.mqtt`)
3. **Multi-Broker Access**: All brokers accessible by name via `cfg.mqtt_configs` dictionary
4. **Backward Compatibility**: Single-broker configs still work without code changes
5. **Connection Management**: Each broker connects and disconnects independently
6. **Default Handling**: Missing config files get sensible defaults

## Test with CI/CD

To run tests in continuous integration:

```bash
# Install dependencies (including dev/test packages)
python -m pip install -e ".[dev,notebooks]"

# Run tests
python -m pytest tests/ -v --tb=short

# With coverage report
python -m pytest tests/ --cov=src/simulated_city --cov-report=html
```

## Troubleshooting

### Tests skip with "MQTT broker not available"

Ensure Mosquitto is running:

```bash
# Start Mosquitto (if installed via Homebrew)
mosquitto &

# Or on macOS with brew services
brew services start mosquitto

# Verify it's listening
lsof -i :1883
```

### Config tests fail with profile not found errors

Check that `config.yaml` exists and has `mqtt.profiles` defined. Tests that write temporary config files should always pass—if they don't, check file permissions.

### Test file syntax errors

Some IDEs may auto-format test files. Verify indentation is correct (4 spaces, no tabs) and that try/finally blocks have proper indentation.

## Contributing Tests

When adding new features:

1. Add test cases to the appropriate module (create new module if needed)
2. Use descriptive test names: `test_<feature>_<scenario>()`
3. Include docstrings explaining what's being tested
4. Run full test suite before committing: `python -m pytest tests/ -v`
5. Update this document if you add new test modules

## Test Dependencies

The test suite requires:

- `pytest` (test framework)
- `paho-mqtt` (MQTT client)
- `pyyaml` (YAML parsing)
- `pyproj` (coordinate transforms)

These are installed with:

```bash
python -m pip install -e ".[dev]"
```
