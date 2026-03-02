# Copilot Instructions (Simulated City Workshop)

This repository is a beginner-friendly workshop template for learning agent-based programming in Python.

**CRITICAL:** These instructions apply to ALL pull requests and code changes. If you are a student working with an AI assistant (including GitHub Copilot), you MUST include this file path in your prompt: `.github/copilot-instructions.md`. If the AI does not follow these instructions, ask it to re-read this file.

## Goals and scope

- Teachability first: simple, explicit control flow and readable code.
- Smallest change that satisfies the requirement; avoid extra features/tooling.
- Documentation-driven development: update docs before behavior changes.
- **No conflicting tools:** `anymap-ts` for mapping (never `folium`, `plotly`, `matplotlib` for live data).
- **Distributed simulations:** Multiple small MQTT-communicating notebooks, never one monolithic notebook.

## Architecture and key modules

- Library code lives in `src/simulated_city/` and intentionally ships only helpers, not a full simulation.
- Configuration is loaded via `simulated_city.config.load_config()`, which searches parent directories for `config.yaml` to support running from `notebooks/`.
- MQTT helpers are in `simulated_city.mqtt` with `connect_mqtt()` and `publish_json_checked()` (self-subscribe publish verifier).
- Optional geospatial helpers live in `simulated_city.geo` (pyproj-backed EPSG transforms).
- CLI smoke entry point is `python -m simulated_city` (see `src/simulated_city/__main__.py`).
- Use anymap-ts for mapping and paho for MQTT client. Avoid extra dependencies to keep it simple.

## Notebook Structure (REQUIRED)

**NEVER** write a monolithic simulation in a single notebook. Instead:

1. **Each agent = separate notebook** (e.g., `agent_transport.ipynb`, `agent_environment.ipynb`)
2. **Agents communicate via MQTT**, not shared memory or files
3. **Dashboard notebook** subscribes to all agents and maps with `anymap-ts`
4. Each notebook calls `mqtt.connect_mqtt()`, subscribes to inputs, runs a loop, publishes outputs

See [docs/exercises.md](docs/exercises.md) for complete examples.

## Forbidden Patterns

❌ **DO NOT:**
- Install `folium`, `plotly`, or `matplotlib` for live/real-time mapping
- Create one big notebook with all simulation logic
- Hardcode MQTT settings or coordinates in notebooks (use `config.yaml`)
- Install packages inside notebooks with `!pip install` (add to `pyproject.toml`)
- Call `subprocess.run(["pip", "install", ...])` in code

✅ **DO:**
- Use `anymap-ts[all]` from `pyproject.toml` for mapping
- Split simulations into independent agent notebooks
- Load config with `simulated_city.config.load_config()`
- Use `mqtt.publish_json_checked()` for verified publishing
- Add dependencies to `pyproject.toml` and install with `pip install -e ".[notebooks]"`

## Configuration and secrets

- Non-secret defaults live in `config.yaml` (MQTT broker host, port, TLS, base topic).
- Secrets are loaded from `.env` (gitignored). MQTT credentials are resolved via env var names in `config.yaml`.

## Developer workflows

- Install: `pip install -e ".[dev,notebooks]"` (add `.[geo]` for CRS helpers).
- Tests: `python -m pytest` (see `tests/` for minimal sanity checks).
- Notebooks: `python -m jupyterlab`.

## Code conventions

- Prefer dataclasses for config containers (see `MqttConfig`, `AppConfig`).
- Public modules/functions/classes should have short, beginner-friendly docstrings.
- Comment the “why” for rules/assumptions in simulations; avoid obvious comments.

## Documentation-driven development

- Update `docs/` first: `docs/overview.md`, `docs/setup.md`, `docs/mqtt.md`, `docs/exercises.md` depending on the change.
- Then implement code updates and add or adjust a small test in `tests/` if relevant.

### PR requirement (always)

Include this line in PR descriptions:

```
Docs updated: yes/no
```

If yes, list doc paths (example: `docs/mqtt.md`). If no, add one sentence why not.

# Project documentation writing guidelines

## General Guidelines
- Write clear and concise documentation.
- Use consistent terminology and style.
- Include code examples where applicable.

## Grammar
* Use present tense verbs (is, open) instead of past tense (was, opened).
* Write factual statements and direct commands. Avoid hypotheticals like "could" or "would".
* Use active voice where the subject performs the action.
* Write in second person (you) to speak directly to readers.

## Markdown Guidelines
- Use headings to organize content.
- Use bullet points for lists.
- Include links to related resources.
- Use code blocks for code snippets.

---

# Enforcing These Instructions

## For Students

If an AI (including GitHub Copilot) suggests code that violates these rules, **reject it and request correction**. Here's how:

**When prompting the AI, always include:**

```
Please follow .github/copilot-instructions.md and:
1. Use anymap-ts (not folium) for mapping
2. Create separate agent notebooks communicating via MQTT (not one big notebook)
3. Load configuration from config.yaml via simulated_city.config.load_config()
4. Add dependencies to pyproject.toml (not pip install in notebooks)
```

**If the AI suggests `folium`, `matplotlib`, or `plotly` for real-time data:**

Say:
> "No, we use anymap-ts for mapping. Please rewrite using anymap-ts from simulated_city and MQTT subscriptions."

**If the AI creates a monolithic notebook:**

Say:
> "Split this into separate notebooks. Each agent (transport, environment, etc.) should be its own notebook that publishes/subscribes via MQTT. See docs/exercises.md for examples."

**If the AI suggests `!pip install` inside a notebook:**

Say:
> "Don't install packages in notebooks. Add the dependency to pyproject.toml and I'll run `pip install -e ".[notebooks]"`."

---

## Model-Agnostic Approach (Any AI Model Works)

**This workshop is designed to work with any AI model** — including when using GitHub Copilot with "auto" model selection. The key is structured prompting and local validation:

### Why This Works With Any Model

1. **Artifacts as source of truth** — The documentation (README, approved design) is more important than any single AI response
2. **Phase-gating** — Implementing one phase at a time means each prompt is self-contained with full requirements
3. **Local validation** — You run `python scripts/validate_structure.py` after each phase, which catches violations before submission
4. **Explicit rules in every prompt** — Each AI request includes the full list of constraints from `.github/copilot-instructions.md`

### If Model Behavior Changes (Model Switching)

If your school switches AI models or you use "auto" selection:

1. **The workflow is unchanged** — Still use the same 3-step process (clarify → plan → implement phases)
2. **Embed constraints in every prompt** — Copy the rules section above into each request
3. **Run validation after each phase**:
   ```bash
   python scripts/verify_setup.py        # Check dependencies
   python scripts/validate_structure.py  # Check code structure
   python -m pytest                      # Run tests
   ```
4. **If a new model violates rules** — Use the corrections from "Common AI Mistakes" section in [STUDENT_GUIDE.md](STUDENT_GUIDE.md)

**Model recommendations** (not required, but helpful):
- **Claude** — Excellent at structured prompts, follows rules precisely
- **GPT-4** — Good at phased thinking, proposes well-scoped phases
- **GitHub Copilot** — Works well with explicit constraints in each prompt

But any model can work if you enforce the workflow and validate locally.

---

## For Instructors

If a student submits code that violates these rules:

1. **Check the PR description**. Does it reference the phased workflow?
2. **Run the validation**:
   ```bash
   python scripts/verify_setup.py
   python scripts/validate_structure.py
   python -m pytest
   ```
3. **In code review**, link to the specific section in copilot-instructions.md:
   > "This uses folium, which violates `.github/copilot-instructions.md#forbidden-patterns`. Please rewrite using anymap-ts."
4. **If multiple students have the same error** — They're probably being given bad prompts by an AI model. Show them [STUDENT_GUIDE.md](STUDENT_GUIDE.md) and the "Common AI Mistakes" section.

---

## If an AI Model Refuses to Follow Instructions

If an AI says "I don't see a copilot-instructions.md file" or ignores it:

1. **Explicitly paste** the relevant section from the file into your prompt
2. **Quote the rule**: "Your instructions say: 'use anymap-ts for mapping (never folium)'"
3. **Request re-work**: "Please rewrite this code to comply with these requirements"
4. **Run validation** to catch violations the AI missed:
   ```bash
   python scripts/validate_structure.py
   ```
5. **If the AI continues to ignore explicit requirements**, inform your instructor — the model may need to be replaced or the prompting approach refined.

---
