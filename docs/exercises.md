# Exercises

This guide shows how to build a multi-agent simulation using separate MQTT-communicating notebooks.

## Principle: Many Small Notebooks, Not One Big File

Each agent or component is a **separate notebook** that:
- Runs its own simulation logic in a loop
- Publishes state to MQTT topics
- Subscribes to input from other agents via MQTT

This is how real systems work — agents are independent processes.

## Example Structure

```
notebooks/
├── agent_transport.ipynb      # Transport simulation agent
├── agent_environment.ipynb    # Air quality simulation agent  
├── agent_infrastructure.ipynb # Building/utility agent
└── dashboard.ipynb            # Read-only visualization
```

## Exercise 1: Single Agent with MQTT

Create `notebooks/agent_transport.ipynb`:

```python
# Cell 1: Setup
import simulated_city.mqtt as mqtt
import simulated_city.config as config
from time import sleep
import json

cfg = config.load_config()
mqtt_cfg = cfg.mqtt

# Cell 2: Connect to MQTT
client = mqtt.connect_mqtt(mqtt_cfg)

# Cell 3: Simulation loop (run this cell repeatedly or schedule it)
for step in range(100):
    vehicle_count = 50 + step % 20  # Simple simulation
    traffic_data = {
        "step": step,
        "vehicles_on_road": vehicle_count,
        "avg_speed_kmh": 45 - (vehicle_count / 10)
    }
    
    # Publish to MQTT
    mqtt.publish_json_checked(
        client, 
        f"{mqtt_cfg.base_topic}/transport/status", 
        traffic_data
    )
    
    sleep(1)
```

**Key points:**
1. Each notebook is independent
2. Configuration is loaded from `config.yaml`
3. Uses `mqtt.connect_mqtt()` and `mqtt.publish_json_checked()`
4. Publishes to a unique topic like `base_topic/transport/status`

## Exercise 2: Multiple Agents (Distributed Simulation)

Create `notebooks/agent_environment.ipynb` that **reads** transport data and **publishes** air quality:

```python
# Cell 1: Setup
import simulated_city.mqtt as mqtt
import simulated_city.config as config
from time import sleep
import json

cfg = config.load_config()
mqtt_cfg = cfg.mqtt

# Cell 2: Subscribe to transport data
def on_transport_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    print(f"Transport vehicles: {payload['vehicles_on_road']}")
    # Store in a variable for use

latest_vehicle_count = 0

def on_message(client, userdata, msg):
    global latest_vehicle_count
    if "transport" in msg.topic:
        payload = json.loads(msg.payload.decode())
        latest_vehicle_count = payload['vehicles_on_road']

# Cell 3: Connect and subscribe
client = mqtt.connect_mqtt(mqtt_cfg)
client.on_message = on_message
client.subscribe(f"{mqtt_cfg.base_topic}/transport/status")

# Cell 4: Simulation loop (depends on transport data)
for step in range(100):
    # Air quality = function of vehicle count
    pm25 = 10 + (latest_vehicle_count * 0.5)  # Vehicles → pollution
    
    air_quality = {
        "step": step,
        "pm25_ug_m3": pm25,
        "vehicles_detected": latest_vehicle_count
    }
    
    mqtt.publish_json_checked(
        client,
        f"{mqtt_cfg.base_topic}/environment/air_quality",
        air_quality
    )
    
    sleep(1)
```

## Exercise 3: Dashboard with `anymap-ts`

Create `notebooks/dashboard.ipynb` to visualize both agents:

```python
# Cell 1: Setup
import simulated_city.mqtt as mqtt
import simulated_city.config as config
from anymap_ts.jupyter import IPythonDisplay
import json

cfg = config.load_config()
mqtt_cfg = cfg.mqtt

# Cell 2: Create map
map_display = IPythonDisplay(center=[51.5, -0.1], zoom=12)
map_display.show()

# Cell 3: Update map from MQTT
latest_data = {"transport": {}, "environment": {}}

def on_message(client, userdata, msg):
    global latest_data
    payload = json.loads(msg.payload.decode())
    
    if "transport" in msg.topic:
        latest_data["transport"] = payload
    elif "environment" in msg.topic:
        latest_data["environment"] = payload
    
    # Update map
    update_display()

def update_display():
    # Clear and redraw markers
    map_display.clear()
    
    if latest_data.get("transport"):
        vehicles = latest_data["transport"].get("vehicles_on_road", 0)
        map_display.add_marker(
            [51.5, -0.1],
            properties={"title": f"Vehicles: {vehicles}"}
        )

# Cell 4: Connect and subscribe
client = mqtt.connect_mqtt(mqtt_cfg)
client.on_message = on_message
client.subscribe(f"{mqtt_cfg.base_topic}/#")  # Subscribe to all

# Cell 5: Keep listening
import time
while True:
    time.sleep(1)
```

## Checklist Before Submitting

- [ ] Each agent is a **separate notebook** (not one giant file)
- [ ] Each notebook publishes to a unique MQTT topic
- [ ] Dashboard or main notebook **subscribes** to agent topics
- [ ] Used `anymap-ts` for visualization (not `folium` or `matplotlib`)
- [ ] Used `mqtt.connect_mqtt()` and `mqtt.publish_json_checked()`
- [ ] Configuration loaded via `config.load_config()`
- [ ] Ran `python scripts/verify_setup.py` (all ✅)
- [ ] All dependencies in `pyproject.toml` (no inline `pip install`)

## Common Mistakes

**Mistake:** One notebook with all simulation code  
**Fix:** Split into agent notebooks that communicate via MQTT

**Mistake:** Using `folium` or `matplotlib` for real-time data  
**Fix:** Use `anymap-ts` which is built for live MQTT feeds

**Mistake:** Hardcoded MQTT settings in notebook  
**Fix:** Use `config.load_config()` to load from `config.yaml`

**Mistake:** Installing packages inside notebooks with `!pip install`  
**Fix:** Add to `pyproject.toml` and reinstall with `pip install -e ".[notebooks]"`
