# Prompt Templates for AI-Assisted Development

Copy-paste these into your AI chat. Don't modify them unless your instructor approves.

---

## Understanding AI Modes

**CRITICAL:** Always tell the AI which mode to operate in. Include this at the start of every prompt:

### Three Operating Modes

1. **ASK MODE** - AI asks clarifying questions, validates assumptions, does NOT design or implement
   - Use when: You have a vague idea and need help refining it
   - AI behavior: Asks questions, points out gaps, does NOT propose solutions yet

2. **PLAN MODE** - AI plans and designs, does NOT implement code
   - Use when: Requirements are clear and you need a structured plan
   - AI behavior: Proposes phases, describes files/tests, does NOT write code

3. **AGENT MODE** - AI implements code based on approved plan
   - Use when: Design is approved and you're ready for one specific phase
   - AI behavior: Writes code, creates notebooks, implements exactly what was approved

### Why This Matters

Without explicit mode instructions, the AI may:
- Write code when you only wanted clarification (wrong mode)
- Ask questions when you're ready to implement (wrong mode)
- Implement multiple phases at once (wrong scope)

**Solution:** Every prompt below starts with "MODE: [ASK/PLAN/AGENT]" — copy it exactly.

---

## Architectural Planning: Notebook vs Library Code

**When to use notebooks** (notebooks/*.ipynb):
- Simulation loops (while True: ... sleep())
- MQTT subscriptions and event handlers
- Agent-specific behavior (one agent = one notebook)
- Dashboard/visualization code

**When to use library code** (src/simulated_city/*.py):
- Reusable data models (dataclasses for Vehicle, Sensor, etc.)
- Utility functions used by multiple notebooks
- Complex calculations or algorithms
- Configuration schemas
- Anything that can be tested with pytest

**Classes vs Functions:**
- Use **classes** for: Agents with state, data models (Vehicle, Sensor), services
- Use **functions** for: Simple helpers, transformations, one-off calculations

**During Phase 1-2 planning, the AI should identify:**
1. Which notebooks to create (e.g., `agent_transport.ipynb`, `dashboard.ipynb`)
2. Which classes belong in library (e.g., `src/simulated_city/models.py` with `Vehicle` class)
3. Which utilities belong in library (e.g., helper functions in existing modules)

This prevents putting everything in notebooks (hard to test, hard to reuse).

---

## Template 1: Design Clarification (Phase 1)

**Use this when:** You have a rough idea and want AI to clarify it.

```
MODE: ASK

I want to build a simulated city based on this outline. 
Please help me clarify it BEFORE I write any code.

You are operating in ASK mode:
- Ask clarifying questions
- Validate my assumptions
- Point out ambiguities
- Do NOT design solutions yet
- Do NOT write code

## My Project
[Copy the 4-component template from README.md and fill it in]

Please:
1. Rewrite the 4 components (Trigger, Observer, Control, Response) using clear technical language
2. Identify the MQTT topics each agent will publish to and subscribe to
3. List any configuration parameters (MQTT broker host/port, GPS coordinates, thresholds, etc.)
4. Identify which notebooks to create (one notebook per agent type)
5. Identify what can be modeled as classes (data models, agent logic) vs simple functions
6. Suggest what belongs in library code (src/simulated_city/) vs notebooks
7. Point out any ambiguities, missing details, or assumptions I've made
8. Suggest realistic starting values for parameters (e.g., how many vehicles, pollution levels)

Do NOT write any code. Just clarify the design.

When you're done, I'll read your clarification and ask for an implementation plan.
```

---

## Template 2: Implementation Planning (Phase 2)

**Use this when:** Design is clear and you're ready for a phased implementation plan.

```
MODE: PLAN

Great! Now that the design is clear, please propose a phased implementation plan.

You are operating in PLAN mode:
- Describe phases and structure
- List files, tests, dependencies
- Do NOT write any code yet
- Do NOT implement anything yet

## Clarified Design
[Paste the clarified design from Template 1 response]

Please propose a phased implementation (5-6 phases):
- Phase 1: Minimal working example (one agent, basic logic)
- Phase 2: Add configuration file (config.yaml)
- Phase 3: Add MQTT publishing
- Phase 4: Add second agent with MQTT subscription
- Phase 5: Add dashboard visualization
- Phase 6: [Any additional phases needed]

For EACH phase, provide:
1. **New files:** What notebooks or library modules (src/simulated_city/) will be created/modified
2. **Architecture:** Which code goes in notebooks (simulation loops, MQTT subscriptions)? Which goes in library (reusable classes, utilities, data models)?
3. **Classes vs functions:** What should be modeled as a class? What's just a helper function?
4. **Tests/Verification:** What commands should I run to verify this phase works
5. **Investigation:** What should I understand/investigate before moving to the next phase
6. **Dependencies:** Any new packages needed (e.g., jupyterlab, anymap-ts)

Do NOT write any code or notebooks yet. Just describe the phases.

When you're done, I'll review the plan and ask for Phase 1 implementation.
```

---

## Template 3: Phase 1 Implementation (Phase 3)

**Use this when:** You've approved the implementation plan and are ready for Phase 1 code.

```
MODE: AGENT

Good! I approve the plan. Now implement ONLY Phase 1:

You are operating in AGENT mode:
- Write code and create files
- Implement only what's described in Phase 1
- Do NOT ask permission
- Do NOT plan other phases
- Do NOT jump ahead to Phase 2+

## Phase 1 (from the approved plan)
[Paste only the Phase 1 description from the plan]

## Rules (from .github/copilot-instructions.md)
These are non-negotiable:
1. Use anymap-ts for mapping (NEVER folium, matplotlib, or plotly for real-time data)
2. Each notebook represents ONE agent (NEVER combine multiple agents in one notebook)
3. Load configuration via simulated_city.config.load_config() (never hardcode values)
4. Use mqtt.publish_json_checked(client, topic, data) for verified publishing
5. Use mqtt.connect_mqtt(mqtt_config) to connect
6. Add all dependencies to pyproject.toml FIRST, run: pip install -e ".[notebooks]"
   (NEVER use !pip install inside notebooks)
7. Start with comments explaining each cell's purpose

DO NOT:
- Create a monolithic notebook
- Ask for phases 2-6 yet
- Suggest installing folium or matplotlib for real-time data
- Hardcode MQTT settings or coordinates
- Suggest !pip install inside the notebook code

Only implement Phase 1. Stop here.

Create a new cell with the code, or create a new notebook file. Include comments.
```

---

## Template 4: Next Phase Implementation

**Use this when:** Phase N is working and you're ready for Phase N+1.

```
MODE: AGENT

Good! Phase 1 works. Now implement ONLY Phase 2:

You are operating in AGENT mode:
- Write code for Phase 2 only
- Do NOT modify Phase 1 unless necessary
- Do NOT ask permission
- Do NOT jump to Phase 3+

## Phase 2 (from the approved plan)
[Paste only the Phase 2 description from the plan]

## Phase 1 Artifacts
These were created in Phase 1:
[List the notebooks/files created - e.g., notebooks/agent_transport.ipynb]

Do NOT modify Phase 1 code unless absolutely necessary.

Remember the rules from Template 3.

Only implement Phase 2. Stop here.
```

---

## Template 5: Bug Fix or Clarification

**Use this when:** Code from previous phase has an error.

```
MODE: AGENT

The code from [Phase X] has a problem:

[Describe the error or unexpected behavior]

Please fix it while keeping the same overall structure.

Remember:
- Don't change the design (that was already approved)
- Don't jump to other phases
- Don't add new features
- Just fix the specific issue

[Paste the problematic code]
```

---

## Rules to Paste Into Every Prompt

If the AI ever ignores the templates above, paste this:

```
RULES from .github/copilot-instructions.md:
❌ DO NOT:
- Install folium, plotly, or matplotlib for real-time maps (use anymap-ts)
- Create one big notebook with all agents (split into separate notebooks)
- Hardcode MQTT settings (use config.yaml)
- Use !pip install inside notebooks (add to pyproject.toml)
- Call subprocess.run(["pip", "install", ...])

✅ DO:
- Use anymap-ts[all] from pyproject.toml for mapping
- Split simulations into agent notebooks (each publishes/subscribes via MQTT)
- Load config via: simulated_city.config.load_config()
- Use: mqtt.publish_json_checked(client, topic, data)
- Add dependencies to pyproject.toml, then: pip install -e ".[notebooks]"
```

---

## After AI Gives You Code

1. **Copy the code into your notebook or create a new file**
2. **Run validation:**
   ```bash
   python scripts/verify_setup.py
   python scripts/validate_structure.py
   python -m pytest
   ```
3. **Test manually:**
   ```bash
   python -m jupyterlab
   # Open the notebook, run all cells, verify it works
   ```
4. **Understand the code:**
   - Can you explain what each cell does?
   - Does it match the design?
   - Does it match Phase X description?

5. **If it works:** Approve and move to next phase
6. **If it doesn't work:** Use Template 5 to ask for fixes

---

## Common Mistakes During Each Phase

### Mode Violations (Most Common Error)
- ❌ AI writes code in ASK mode → **Reject:** "You're in ASK mode. Do NOT write code. Just ask questions."
- ❌ AI asks permission in AGENT mode → **Reject:** "You're in AGENT mode. Implement it, don't ask."
- ❌ AI implements in PLAN mode → **Reject:** "You're in PLAN mode. Describe the plan, don't implement."

### Phase 1: Design Clarification (ASK Mode)
- ❌ AI writes code → **Reject:** "You're in ASK mode. No code yet. Only ask clarifying questions."
- ❌ AI proposes 5 phases at once → **Reject:** "You're in ASK mode. Just ask questions about my design."

### Phase 2: Planning (PLAN Mode)
- ❌ AI writes code → **Reject:** "You're in PLAN mode. Just describe the phases. I'll approve before implementation."

### Phase 2: Planning (PLAN Mode)
- ❌ AI writes code → **Reject:** "You're in PLAN mode. Just describe the phases. I'll approve before implementation."
- ❌ AI doesn't specify architecture → **Ask:** "Which notebooks? Which classes in src/simulated_city/? Notebook vs library code?"
- ❌ AI skips a phase → **Ask:** "Can you add a phase for X?"
- ❌ Phase descriptions are vague → **Reject:** "More specific. What files? What tests?"

### Phase 3+: Implementation (AGENT Mode)
- ❌ AI asks "Should I implement this?" → **Reject:** "You're in AGENT mode. Implement it now."
- ❌ AI uses folium → **Reject:** "Use anymap-ts. Rewrite it."
- ❌ AI creates one giant notebook → **Reject:** "Split this into separate agent notebooks."
- ❌ AI suggests `!pip install` → **Reject:** "Add to pyproject.toml instead."
- ❌ AI hardcodes MQTT settings → **Reject:** "Use config.yaml and config.load_config()."
- ❌ AI implements Phase 2 when asked for Phase 1 → **Reject:** "Only Phase 1. Stop here."

---

## Troubleshooting

**Q: AI operates in wrong mode (writes code when I want questions, or asks when I want code)**  
A: Paste this: "You are in [ASK/PLAN/AGENT] mode. Re-read the mode instructions in my prompt."

**Q: AI says "I don't see the copilot-instructions file"**  
A: Paste the Rules section above into your next message.

**Q: Validation scripts fail**  
A: Ask AI to fix the specific error using Template 5.

**Q: Code runs but seems wrong**  
A: Ask your instructor or re-read docs/exercises.md for examples.

**Q: Can I skip phases?**  
A: No (unless instructor approves). Each phase teaches something. Skipping breaks the learning.

---

## When the AI Model Changes (Auto Selection)

If your school switches models, use the **same templates**. The workflow is model-agnostic.

The validation scripts will catch violations no matter which model wrote the code.
