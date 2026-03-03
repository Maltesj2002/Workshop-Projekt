# simulated-city-template

This is a template repository.

Get started by reading [docs/setup.md](docs/setup.md).
See [docs/overview.md](docs/overview.md) for an overview of the base module content.

## Template for a project
---

## Workflow: Document-Driven Development with AI
### My Smart City Project: [Simulation of surveillance in cities]

#### 1. The Trigger (Who/What is moving?)
Describe the **Agents** (Humans, Animals, Vehicles) and the **Surroundings** (Weather, Time).
The Agents are:
10 Different Humans
Each human has:
First and Last name
Unique ID(Could be their names)
A criminal count that starts at zero
A random but unique marker color
The unique marker color is only active initially until criminal acts have been detected

Movement rules of the agents:
Each human moves randomly
One timestep = one real time second
Step length = 7 meters
Direction = random angle
New position = old position + movement vector
Simulation shouldn’t be reproducible
They should move even if they commit an event
The movement should be continuous 

If movement would place the human outside the 1000x1000 boundary:
Reflect direction
If they hit a corner reflect on both axes
Reflect the overshoot distance back into the map
Reflection applies seperately pr. axis(x,y) with overshoot mirrored back into [0,1000]

Illegal Event Probability:
Each human has a 25% chance of committing an illegal act each step
Events are checked immediately in the same step they are created
Multiple humans can create an event in the same timestep
Humans can create max 1 event pr. timestep
The event type should always be the same
If illegal event occurs:
Create an Event object at the humans current position 
Event is processed only in the creation timestep

Surroundings:
They should be moving around a 1000x1000 meter area.
The center of the area is Parken Stadion in Copenhagen.
The humans should be placed randomly within the 1000x1000 meter area 
The map should be pulled from “anymap”. 
The map is only visual and shouldn’t affect the humans movement.
Movement should be in a local 1000x1000 meter simulation centered at parken, with map used for visualisation(map is pulled from anymap)
The simulation should run at real wall-clock speed = 1 timestep pr. second
The timestamp format should be in simulation step index

#### 2. The Observer (What does the city see?)
What **Sensor** picks up the information? 
Cameras must collectively cover 35% of the total area.
Total area = 1000 × 1000 = 1,000,000 m²
Required coverage = 350,000 m²
Is implemented by: 
Divide the map into a 100x100 grid
Cell size = 1000/100 = 10m × 10m
Convert position to cell:
•	cell_x = floor(x / 10)
•	cell_y = floor(y / 10)
If x=1000 or y=1000 exactly, clamp to 99.
Randomly mark 35% of cells as “camera-covered”
The camera cells should be fixed after initialization
The camera grid should be random each run
Draw covered cells as a semi-transparent overlay
When an illegal event occurs:
1.	Check if event position is inside a camera-covered area
2.	If yes:
Trigger alarm
Record:
Human name
Timestamp
Camera detects + publishes; Registry increments criminal_count
Add human to criminal list (if not already there)
No false positives required 
Trigger alarm = Show a blinking red marker for 1 step
This should be separate from the human marker color state
#### 3. The Control Center (The Logic)
How does the city "think" about this information?
Criminal Registry:
A dictionary or list structure:
criminal_registry = {
    human_id: {
        name: "First Last",
        criminal_count: integer
    }
}
Whenever a camera detects an illegal event:
•	Update registry
•	Increase criminal count
Human_ID = exactly the full name string and therefore unique pr. human
Only detected crimes are counted
#### 4. The Response (What happens next?)
What is the **Controller** that changes the city?
Visual Response:
criminal_count == 0 → unique color
If human.criminal_count > 0:
•	Change marker color from unique color to red
If human.criminal_count > 10:
•	Change marker color from red to black
This visually represents:
•	The city labeling individuals
•	Algorithmic classification

Criminal_count increases only when detected by camera

#### 5. Simulation loop
Pseudo-structure:

initialize map
initialize 10 humans
initialize camera coverage
initialize empty criminal registry

for each timestep:
    for each human:
        move human
        if random() < 0.25:
            create illegal event
            if event inside camera area:
                registry registrates criminal_count
                registry updates
                change marker to red

    render map
    render humans
    render camera coverage
    update statistics

#### 6. Agent split
Each notebook is independent and communicates only via MQTT topics.
Four seperate notebooks:
1. Human movement/event producer
2. Camera Detector
3. Registry/control center
4. Dashboard visualizer

Additional agent rules:
- On startup/restart, each notebook starts in **cold-start mode** (no retained replay assumed, because live topics use `retain=false`).
- Each notebook processes only new live messages after it reconnects.
- All notebooks load broker/topic/runtime settings via `simulated_city.config.load_config()` from `config.yaml` (no hardcoded MQTT settings in notebooks).


#### 7. MQTT Contract (Agent Communication)

Base topic:
- `simcity/surveillance`

Topics:

1. `simcity/surveillance/humans/state`
   - Publisher: Human movement/event producer
   - Subscribers: Dashboard visualizer (optional: Camera detector)
   - Purpose: Live movement state
   - Payload (minimum): `step`, `human_id`, `name`, `x`, `y`
   - Optional mirrored fields: `criminal_count`, `marker_color` (non-authoritative)

2. `simcity/surveillance/events/illegal`
   - Publisher: Human movement/event producer
   - Subscribers: Camera detector, Dashboard visualizer
   - Purpose: Illegal events created by humans
   - Payload (minimum): `step`, `event_id`, `human_id`, `x`, `y`, `event_type`

3. `simcity/surveillance/detections/camera`
   - Publisher: Camera detector
   - Subscribers: Registry/control center, Dashboard visualizer
   - Purpose: Camera detection decision pr. event
   - Payload (minimum): `step`, `event_id`, `human_id`, `camera_cell`, `detected`

4. `simcity/surveillance/registry/updates`
   - Publisher: Registry/control center
   - Subscribers: Dashboard visualizer
   - Purpose: Official criminal/accounting updates (source of truth)
   - Payload (minimum): `step`, `human_id`, `name`, `criminal_count`

5. `simcity/surveillance/alarms/active`
   - Publisher: Camera detector
   - Subscribers: Dashboard visualizer
   - Purpose: Visual alarm stream only
   - Payload (minimum): `step`, `event_id`, `human_id`, `x`, `y`, `ttl_steps`

Rules:
- Use `step` as simulation timestamp format.
- `step` starts at `0` and increments by `1` every timestep.
- `human_id` is exactly the full name string.
- `event_type` is always `"illegal_act"`.
- Every illegal event has a unique `event_id`.
`event_id` format is locked to `"{step}:{human_id}"`
- Consumers deduplicate by `event_id` and ignore duplicates.
- Events are valid only in the creation timestep.
- `criminal_count` increases only on camera-detected events after registry processing.
- consumers process only messages where `message.step == local_current_step`; messages with lower or higher step are ignored.

#### 7.1 Protocol decisions (locked)

These decisions are final for this project:

1. **Registry is source of truth**
   - Registry/control center is the only component that updates criminal state (`criminal_count`).
   - Camera detector, producer, and dashboard treat criminal state as read-only data from `simcity/surveillance/registry/updates`.

2. **Alarm ownership split**
   - Camera detector publishes visual alarm events on `simcity/surveillance/alarms/active`.
   - Registry/control center updates criminal records and publishes `simcity/surveillance/registry/updates`.

3. **`camera_cell` format**
   - Use JSON array format: `[cell_x, cell_y]`.

4. **`event_type` constant**
   - Always use `"illegal_act"`.

5. **Step indexing**
   - `step` starts at `0` and increments by `1` pr. timestep.

6. **MQTT live-stream delivery**
   - Use `qos=0` and `retain=false` for:
     - `humans/state`
     - `events/illegal`
     - `detections/camera`
     - `alarms/active`
     - `registry/updates`

7. **Event identity and deduplication**
   - Every illegal event has a globally unique `event_id`.
   - `event_id` format is `"{step}:{human_id}"`.
   - Consumers deduplicate by `event_id` and ignore duplicates.

8. **Late/out-of-order handling**
   - Consumers ignore messages that are older than the current processed step window.
    - Messages with `step < local_current_step` are dropped as late.
   - Messages with `step > local_current_step` are dropped as out-of-order.

   9. **Restart behavior**
   - Agents are independently restartable and resume in cold-start mode.
   - No retained replay is required for live topics (`retain=false`).

10. **Configuration source**
   - All agents load settings from `config.yaml` via `simulated_city.config.load_config()`.
   - Hardcoded broker/topic values are not allowed.

#### 7.2 Topic responsibility clarification

- `simcity/surveillance/humans/state` = movement/identity stream.
- `simcity/surveillance/events/illegal` = illegal-event creation stream.
- `simcity/surveillance/detections/camera` = camera decision stream.
- `simcity/surveillance/alarms/active` = visual alert stream from Camera detector.
- `simcity/surveillance/registry/updates` = official criminal/accounting stream from Registry/control center.

Authority rules:
- Criminal state authority is only `simcity/surveillance/registry/updates`.
- Alarm visuals are independent of person marker color state.
- Marker color logic is derived from authoritative `criminal_count`:
  - `0` → unique initial color
  - `1..10` → red
  - `>10` → black

Do NOT write any code. Just clarify the design.
```

#### Review the AI's response
- Does it capture your idea correctly?
- Are the agents clearly separated?
- Are the MQTT topics clear?
- If not, refine and ask again

---

### Phase 2: Get an Implementation Plan (Still No Code)

#### Once you agree on the design, use this prompt:

```
Based on the design we just clarified:

[Paste the clarified design from Phase 1]

Please propose a phased implementation plan:
- Phase 1: Single basic agent (smallest working notebook)
- Phase 2: Add configuration file
- Phase 3: Add MQTT publishing
- Phase 4: Add second agent with MQTT subscription
- Phase 5: Add dashboard visualization

For each phase:
1. List what new notebook files will be created
2. List what tests/verifications I should run
3. Say exactly what I should investigate/understand before moving to the next phase

Do NOT write code yet. Just show the phases.
```

#### Review and approve the plan
- Does each phase test one new thing?
- Can you run and understand each phase?
- Are there gaps?
- Ask AI to adjust if needed

---

### Phase 3: Implement ONE Phase at a Time

#### For the FIRST phase only, use this prompt:

```
Implement ONLY Phase 1 from the plan below:


Plan: Phase 1 Humans Producer (No MQTT)
Phase 1 is scoped correctly and can proceed as a single-agent notebook only. In this planning mode, I won’t implement files directly, but this is the exact execution spec for Phase 1 with verification and investigation gates.

Steps

Create notebooks/agent_humans_producer.ipynb with clearly commented sections: setup/imports, config load, human initialization, movement/reflection logic, event generation, 1 Hz loop, and visualization.
Use simulated_city.config.load_config() from config.py for runtime settings; keep simulation non-reproducible (no fixed RNG seed).
Implement only local movement + event generation (event_type="illegal_act", max 1 event per human per step, event_id="{step}:{human_id}"), with no MQTT publish/subscribe in this phase.
Use anymap-based visualization only (no folium/matplotlib/plotly), keeping map visual-only and movement in local 1000x1000 meters.
Keep one notebook = one agent (no camera/registry/dashboard logic in this phase).
Verification

Run python scripts/verify_setup.py
Run python scripts/validate_structure.py
Run manual notebook execution in Jupyter (Run All) and confirm steady 1-second timestep behavior.
Investigate before Phase 2

Reflection correctness on edges/corners with overshoot mirroring into [0,1000].
Actual loop cadence near 1 Hz under notebook execution load.
event_id uniqueness in practice across many steps/humans.
Phase rule note: mqtt.publish_json_checked() is not used in Phase 1 because MQTT is out of scope here.

Remember these rules (from .github/copilot-instructions.md):
- Use anymap-ts for mapping (NOT folium)
- Each notebook is ONE agent (NOT monolithic)
- Load config via simulated_city.config.load_config()
- Use mqtt.publish_json_checked() for publishing
- Add all dependencies to pyproject.toml (NOT !pip install in notebooks)

Only implement Phase 1. Do NOT jump ahead to Phase 2.
Include comments explaining each section.
```

#### After you get the code:
```bash
python scripts/verify_setup.py      # Check dependencies
python -m pytest                     # Run tests
python -m jupyterlab                # Open the notebook and RUN IT
```

#### Investigate before moving forward
- Does the notebook actually run without errors?
- Can you explain what each cell does?
- Does it match the design from Phase 1?
- If something is wrong, ask AI to fix it before moving to Phase 2

---

### Phase 4: Move to the Next Phase

Once Phase 1 works, use this prompt:

```
Good! Phase 7 works. Now implement ONLY Phase 8:
Phase 8 Cross-phase hardening — add registry/control center when Phase 4 is stable: create notebooks/agent_registry_control.ipynb; verify end-to-end topic authority (registry/updates as truth), dedup by event_id, and restart cold-start behavior; investigate mismatch risks between mirrored criminal_count in humans/state and authoritative registry values.

Plan: Phase 8 Registry/Control Hardening (DRAFT)
Phase 8 will add only one new notebook agent, notebooks/agent_registry_control.ipynb, and keep Phase 1–7 files unchanged. The new registry agent will subscribe to camera detections (and humans/state for name cache), deduplicate by event_id, enforce strict same-step processing, and publish authoritative counts on simcity/surveillance/registry/updates. It will start in cold-start mode (empty state after restart), process only new live messages, and log mismatch warnings if mirrored criminal_count appears in humans/state and conflicts with authoritative registry values. This matches your locked protocol: registry updates are the only truth source for criminal state.

Steps

Create notebooks/agent_registry_control.ipynb with sections: imports/config, topic constants, runtime state, MQTT callbacks, processing loop, diagnostics, cleanup.
Load config with load_config() and define design-locked topics under simcity/surveillance; subscribe to:
simcity/surveillance/detections/camera (primary input)
simcity/surveillance/humans/state (name cache + mirrored field risk checks)
Add thread-safe callback queue ingestion (no processing in MQTT callback), consistent with prior agent patterns.
Maintain registry state:
criminal_registry[human_id] = {name, criminal_count}
processed_event_ids for dedup
names_by_human_id cache from humans/state
Enforce strict step-window in registry processing (message.step == local_current_step, anchored to first seen step and advanced at 1 Hz), and apply dedup by event_id before any increment.
Increment criminal_count only for detected == true detections; for each increment publish minimum schema to simcity/surveillance/registry/updates:
step, human_id, name, criminal_count
with qos=0, retain=False.
Implement cold-start behavior explicitly:
on notebook start/restart, initialize empty in-memory state
no replay assumptions, process only live incoming messages.
Add Phase 8 diagnostics cells to report:
registry size/counts snapshot
dedup counts / dropped-late / dropped-out-of-order
mismatch warnings when mirrored criminal_count in humans/state differs from authoritative registry count.
Keep all existing notebooks untouched in this phase (producer, detector, dashboard remain as-is).
Verification

Run python scripts/verify_setup.py.
Run python scripts/validate_structure.py.
Run python -m pytest.
Manual end-to-end run:
Start detector notebook subscription cell.
Start new registry notebook subscription/processing cell.
Start dashboard (optional for visual confirmation).
Start producer simulation cell.
Confirm:
only registry/updates carries authoritative count evolution,
duplicate detections for same event_id do not double-increment,
registry restart clears in-memory state (cold-start) and resumes on new live traffic,
mismatch warnings appear when mirrored criminal_count conflicts with registry authority.
Decisions

Name source: cache from humans/state.
Step rule: strict same-step only.
registry/updates schema: minimum fields only (no extra event_id).
Mirrored-count risk handling: log warnings only in Phase 8.




Implement only Phase 8. Do NOT modify Phase 1+2+3+4+5+6+7 code unless necessary.
```

**Repeat this cycle for each phase.**

---

## Key Rules to Remember

✅ **DO** enforce these in every AI prompt:
1. Two separate MQTT topics are better than one shared variable
2. Each agent notebook is independent and can restart anytime
3. Configuration comes from `config.yaml`, not hardcoded values
4. All dependencies go in `pyproject.toml` first, then `pip install -e ".[notebooks]"`
5. Dependencies must be approved: `anymap-ts` ✅, `folium` ❌

❌ **DO NOT** let AI:
- Skip the documentation/planning phases
- Create one giant notebook with all logic
- Jump to implementation without a clear, approved design
- Install packages inside notebooks with `!pip install`
- Use `folium`, `matplotlib`, or `plotly` for real-time maps

---

## If the AI Skips Steps

If you ask for implementation and the AI writes code without clarifying the design first, respond with:

> "No code yet. I need to clarify the design first. Please rewrite my outline using the Phase 1 prompt above, then we'll get a plan before any implementation."

If the AI proposes all 5 phases at once instead of letting you implement one at a time:

> "I need only Phase 1 implementation. We'll do the other phases after I test Phase 1. Just give me Phase 1 code."

If the AI installs `folium` or uses `!pip install`:

> "No, use anymap-ts and add dependencies to pyproject.toml. Also, re-read .github/copilot-instructions.md for the full list of rules."

---

## Testing Your Work

After each phase, run:

```bash
# Check environment
python scripts/verify_setup.py

# Run existing tests
python -m pytest

# Try your new notebook
python -m jupyterlab
# Open the notebook and run all cells
```

Before submitting a pull request, include this in your description:

```
Docs updated: yes/no
Phases completed: [e.g., "Phase 1 and Phase 2"]
Tests passing: yes/no
```