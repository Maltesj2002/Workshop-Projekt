# Student Quick Reference: Document-Driven AI Development

**This guide teaches you how to use AI as a thinking tool, not just a code generator.**

The workflow is the same whether you submit work via GitHub, folder snapshots, or in-person review. Check with your instructor which method your class uses.

## Updating This Guide (If Your Instructor Updates It)

If your instructor updates `STUDENT_GUIDE.md` or `PROMPT_TEMPLATES.md`, you can download just those files without re-cloning your entire repository.

**Quick reference:** See [UPDATING.md](UPDATING.md) for copy-paste commands.

The template repository is: https://github.com/Esbern/simulated-city-template



### Option 1: Using Terminal (macOS / Linux / Git Bash on Windows)

```bash
# From your repository root directory
cd docs

curl -O https://raw.githubusercontent.com/Esbern/simulated-city-template/main/docs/STUDENT_GUIDE.md
curl -O https://raw.githubusercontent.com/Esbern/simulated-city-template/main/docs/PROMPT_TEMPLATES.md

# Go back to repository root
cd ..
```

### Option 2: Using PowerShell (Windows)

```powershell
# From your repository root directory
cd docs


Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Esbern/simulated-city-template/main/docs/STUDENT_GUIDE.md" -OutFile "STUDENT_GUIDE.md"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Esbern/simulated-city-template/main/docs/PROMPT_TEMPLATES.md" -OutFile "PROMPT_TEMPLATES.md"

# Go back to repository root
cd ..
```

### Option 3: Manual Download (Any Platform)

1. Go to **your instructor's repository** on GitHub.com (or the original: https://github.com/Esbern/simulated-city-template)
2. Navigate to `docs/STUDENT_GUIDE.md`
3. Click the "Raw" button
4. Right-click → "Save As..." → Save to your `docs/` folder
5. Repeat for `PROMPT_TEMPLATES.md`

### After Updating

After downloading the updated files, you may want to commit them to your repository:

```bash
git add docs/STUDENT_GUIDE.md docs/PROMPT_TEMPLATES.md
git commit -m "Update documentation guides from instructor"
git push
```

**Tip:** Ask your instructor to announce when these files are updated so you know when to refresh them.

---

## The Workflow (Documentation-First Development)

This workflow creates **reviewable documentation artifacts** before any code is written. Each artifact becomes part of your git history and can be reviewed by your instructor.

```
Step 1 (PLAN mode) → docs/concepts.md
        ↓
Step 2 (PLAN mode) → docs/implementationplan.md
        ↓
Step 3 (AGENT mode) → Code + docs/phase_1_runtime.md
        ↓
    ┌───────────────────────────────┐
    │ Validation Loop (Template 5.5) │
    │                               │
    │ Human: Test & compare         │
    │   ↓                           │
    │ Match? ✅ → Next phase        │
    │   ↓                           │
    │ Mismatch? ❌ → AI fixes       │
    │   ↓                           │
    │ Re-test → Loop until match    │
    └───────────────────────────────┘
        ↓
Step 4 (AGENT mode) → Code + docs/phase_2_runtime.md
        ↓
    [Validation Loop...]
        ↓
    (Continue for each phase)
```

### Step 1: Design Clarification → `docs/concepts.md`

**Goal:** Create a clear design document that captures your project's architecture.

**Mode:** PLAN (AI writes documentation, not code)

Copy the prompt from [Template 1 in PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md#template-1-design-clarification-docsconceptsmd). The AI will create a `docs/concepts.md` file containing:

- Technical rewrite of your 4 components (Trigger, Observer, Control, Response)
- MQTT topics (what each agent publishes/subscribes to)
- Configuration parameters (broker settings, locations, thresholds)
- Architecture decisions (notebook vs library code, classes vs functions)
- List of notebooks to create (one per agent type)

**What you do:**

1. Review `docs/concepts.md`
2. Edit it if needed (you can ask AI to refine specific sections)
3. Commit it to git before moving to Step 2
4. Instructor reviews and approves the design

### Step 2: Implementation Planning → `docs/implementationplan.md`

**Goal:** Create a phased implementation plan based on the approved design.

**Mode:** PLAN (AI writes documentation, not code)

Copy the prompt from [Template 2 in PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md#template-2-implementation-planning-docsimplementationplanmd). The AI will create a `docs/implementationplan.md` file containing:

- Phase breakdown (Phase 1-5+)
- Files to create/modify per phase
- Tests/verification commands per phase
- Dependencies needed
- Investigation tasks between phases

**What you do:**

1. Review `docs/implementationplan.md`
2. Discuss with instructor if phases make sense
3. Edit if needed
4. Commit it to git before moving to Step 3
5. Instructor approves the implementation plan

### Step 3+: Implement ONE Phase at a Time

**Goal:** Write actual code for one approved phase AND document how to run/debug it.

**Mode:** AGENT (AI writes code and documentation)

Copy the prompt from [Template 3 in PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md#template-3-phase-1-implementation-phase-3). The AI will:

- Create notebooks and library code
- Create runtime documentation (e.g., `docs/phase_1_runtime.md`)
- Follow the phase description from `implementationplan.md`
- Apply all rules from `.github/copilot-instructions.md`

**What you do:**

1. **Review the runtime documentation** - Understand expected outputs and workflows
2. **Test the code** - Follow the workflows in the runtime doc
3. **Run validation**: `python scripts/verify_setup.py && python -m pytest`
4. **Validate alignment** - Does implementation match documentation? Use Template 5.5 validation workflow:
   - For each workflow: Compare expected vs actual output
   - Document any mismatches
   - If mismatches exist: Use Template 5.5B to have AI fix alignment
   - Re-test until implementation matches documentation
5. **Debug if needed** - Use the debugging guidance in the runtime doc
6. **Commit both code AND runtime documentation** (only after validation passes)
7. **Create PR**
8. After instructor approval, move to next phase

**Key principle:** Each phase builds on the approved previous phase. Each phase includes runtime documentation showing how to run and debug what was built. **Do NOT move to the next phase until you validate that implementation matches documentation.**

**MQTT debugging tip:** If your project uses MQTT, consider creating a `notebooks/mqtt_monitor.ipynb` notebook that subscribes to all topics (`#` wildcard) and prints all messages. This is invaluable for debugging message flow.

---

## Understanding Architecture: Notebook vs Library Code

One of the most important decisions in Phase 1-2 is **where code should live**:

### Notebooks (notebooks/*.ipynb)
**Use for:**
- Simulation loops (while True: ... sleep())
- MQTT subscriptions and event handlers  
- Agent-specific behavior (one notebook per agent)
- Dashboard/visualization code

**Why:** Notebooks are for running simulations and visualizing results.

### Library Code (src/simulated_city/*.py)
**Use for:**
- Reusable data models (dataclasses: Vehicle, Sensor, etc.)
- Utility functions used by multiple notebooks
- Complex calculations or algorithms
- Configuration schemas
- Anything that needs automated tests (pytest)

**Why:** Library code is for reusable, testable components.

### Classes vs Functions

- **Classes:** For agents with state, data models (Vehicle, Sensor), services
- **Functions:** For simple helpers, transformations, one-off calculations

### Example Architecture

Good design (distributed):
```
notebooks/
  agent_transport.ipynb    # Transport agent: subscribes to traffic, publishes vehicle positions
  agent_environment.ipynb  # Environment agent: simulates pollution based on vehicle data
  dashboard.ipynb          # Visualizes everything on anymap-ts

src/simulated_city/
  models.py               # Vehicle, Sensor dataclasses
  simulation.py           # Helper functions for movement, calculations
```

Bad design (monolithic):
```
notebooks/
  everything.ipynb        # ❌ All agents + dashboard in one file
```

During planning (Step 2), the AI should identify which notebooks and which library modules to create. This makes your code:

- Testable (library code can be tested with pytest)
- Reusable (multiple notebooks can import the same classes)
- Maintainable (each notebook has a clear purpose)

---

## Common AI Mistakes (And How to Fix Them)

### ❌ AI doesn't create documentation files

You: "You're in PLAN mode. Create the docs/concepts.md file with all sections. Don't just describe it."

### ❌ AI writes code when asked for documentation

You: "You're in PLAN mode. Create docs/concepts.md markdown file, not code. No Python files yet."

### ❌ AI asks questions instead of creating concepts.md

You: "You're in PLAN mode. Make reasonable assumptions and create the file. I'll edit it after."

### ❌ AI tries to code without creating implementationplan.md first

You: "We need docs/implementationplan.md first. Use Template 2 from PROMPT_TEMPLATES.md."

### ❌ AI proposes all 5 phases in chat instead of a file

You: "Create docs/implementationplan.md as a markdown file with proper sections for each phase."

### ❌ AI uses folium instead of anymap-ts

You: "No, use anymap-ts. Check .github/copilot-instructions.md for the rules."

### ❌ AI creates one big notebook instead of agent notebooks

You: "Split into separate notebooks. Each agent publishes/subscribes via MQTT. See docs/exercises.md."

### ❌ AI uses !pip install in notebook

You: "Don't install in notebooks. Add to pyproject.toml and run: pip install -e '.[notebooks]'"

### ❌ AI implements wrong phase

You: "Implement only Phase [N] from docs/implementationplan.md. Stop there."

### ❌ AI creates vague expected outputs in runtime doc

You: "Be specific. Don't say 'prints message' - say 'prints: Connected to MQTT broker at localhost:1883'"

### ❌ Implementation doesn't match runtime documentation

You: "I tested using Template 5.5 validation. Here's my report: [paste validation report]. Fix the alignment."

### ❌ AI skips runtime documentation

You: "You must create docs/phase_N_runtime.md with specific expected outputs, workflows, and debugging guidance."

---

## Validation Commands

```bash
# Check dependencies are correct
python scripts/verify_setup.py

# Check code structure (no monolithic notebooks, no folium)
python scripts/validate_structure.py

# Run tests
python -m pytest

# Open notebooks and test manually
python -m jupyterlab
```

---

## If Your Model Switches (Auto Mode)

The workflow is **model-agnostic**. It works with any AI because:
1. You write artifacts (README clarification, approved design)
2. Each prompt is self-contained with full rules embedded
3. You validate output locally before moving forward

If a new model doesn't follow rules, respond with the "Common AI Mistakes" section above.

---

## Submitting Your Work (Using GitHub Desktop & VS Code)

### What is a Pull Request?

A **Pull Request (PR)** is how you submit code for review on GitHub:

1. You work in VS Code (in a branch: separate copy of the project)
2. You commit and sync using VS Code's Source Control panel (or GitHub Desktop)
3. You create a PR on GitHub.com (ask instructor: "Ready for review?")
4. Instructor reviews your code in the PR
5. If approved, your changes merge into the main project

**Why?** This enforces phase-gating. You can't start Phase 2 until Phase 1 is approved.

### The Branch Flow

Here's how phases progress:

```
main branch
  │
  ├── Create phase-1 branch
  │   ├── Code Phase 1
  │   ├── Commit + Sync
  │   └── Create PR → Instructor reviews → Merge into main ✅
  │
  ├── Pull updated main
  │
  ├── Create phase-2 branch
  │   ├── Code Phase 2
  │   ├── Commit + Sync
  │   └── Create PR → Instructor reviews → Merge into main ✅
  │
  └── Repeat for Phase 3, 4, 5...
```

Each phase builds on the previous approved phase.

### Checklist Before You Commit

Before you commit your Phase 1 work:

- [ ] README filled in with 4-component template (your project idea)
- [ ] **docs/concepts.md created and reviewed** ← Design clarification
- [ ] **docs/implementationplan.md created and reviewed** ← Phased plan
- [ ] **Only ONE phase implemented** ← Most important!
- [ ] **docs/phase_N_runtime.md created** ← Runtime documentation with workflows and expected outputs
- [ ] **Tested using workflows in runtime doc** ← Followed the "How to Run" steps
- [ ] **Validated implementation matches documentation** ← Actual outputs match expected outputs
- [ ] **Fixed any mismatches** ← Used Template 5.5B if needed
- [ ] Tests passing: `python scripts/verify_setup.py && python -m pytest`
- [ ] Structure valid: `python scripts/validate_structure.py`
- [ ] PR description references concepts.md, implementationplan.md, and phase_N_runtime.md

### Workflow: VS Code (with GitHub Desktop as alternative)

All Git operations can be done in VS Code. GitHub Desktop is an alternative if you prefer a visual Git interface.

#### Step 1: Create a branch (in VS Code)
```
1. Open VS Code
2. Look at the bottom left corner — you'll see the current branch name (e.g., "main")
3. Click on it
4. Select "+ Create new branch" from the dropdown
5. Type the name: phase-1
6. Press Enter
```

**Alternatively:** You can create the branch in GitHub Desktop:
```
1. Open GitHub Desktop
2. Click "Current Branch" at the top
3. Click "New Branch"
4. Name it: phase-1
5. Click "Create Branch"
6. Then switch back to VS Code
```

#### Step 2: Make your changes (in VS Code)
```
1. Open VS Code
2. Edit/create your notebooks, code, docs
3. Run validation commands in the terminal:
   python scripts/verify_setup.py
   python scripts/validate_structure.py
   python -m pytest
```

#### Step 3: Commit (in VS Code)
```
1. In VS Code, click the Source Control icon (Git icon on the left sidebar)
2. You'll see your changed files listed
3. Click the "+" next to each file to stage it (or click "+" at the top to stage all)
4. Type a commit message in the box: "Phase 1: Basic agent with MQTT"
5. Click the "✓ Commit" button
```

#### Step 4: Sync (in VS Code)
```
1. After committing, click the "Sync Changes" button that appears
   (Or click the ↻ icon at the bottom left)
2. This uploads your changes to GitHub.com
3. First time: VS Code may ask "Publish Branch?" → Click "OK"
```

#### Step 5: Create a Pull Request (on GitHub.com)
```
1. Go to GitHub.com and open your repository
2. You should see a notification: "Compare & pull request"
3. Click it
4. Fill in the PR description (see template below)
5. Click "Create pull request"
```

### What to Put in Your PR Description

When you create the PR, use this template:

```
## What Phase Is in This PR?

Phase 1: Basic agent with MQTT

## Design Documents

- [x] Design clarification: docs/concepts.md
- [x] Implementation plan: docs/implementationplan.md
- [x] Runtime documentation: docs/phase_1_runtime.md

## What I Investigated

[Briefly: what did you learn/test from this phase?]

## Expected Outputs (from runtime doc)

[Copy key expected outputs from docs/phase_N_runtime.md - this helps reviewers verify]

Example:
- Agent notebook cell 3: Should print "Connected to MQTT broker"
- Agent notebook cell 5: Should publish to topic "city/transport/vehicles"
- Dashboard updates every 2 seconds with vehicle positions

## Verification

Ran these commands successfully:
- [x] python scripts/verify_setup.py
- [x] python scripts/validate_structure.py
- [x] python -m pytest
- [x] Manually tested using workflows from docs/phase_N_runtime.md
- [x] **Validated implementation matches documentation** (used Template 5.5 validation)
- [x] All expected outputs match the runtime documentation
- [x] Fixed any mismatches between code and documentation
```

### After Your Instructor Reviews

Your instructor will:
1. Look at your Phase 1 code
2. Run validation scripts
3. Either approve or ask for changes

**If approved:**
1. Instructor clicks "Merge pull request" on GitHub.com
2. Your Phase 1 code is now in the main branch ✅
3. **You** can now start Phase 2:
   ```
   1. In VS Code, switch to main branch (click branch name bottom left)
   2. Click the ↻ sync icon to pull the updated main
   3. Create a new branch: phase-2 (click branch name → "+ Create new branch")
   4. Start implementing Phase 2
   ```

**If changes needed:**
1. Fix them in VS Code (stay on the phase-1 branch)
2. Commit again
3. Sync
4. The PR updates automatically
5. Instructor re-reviews

---

### Quick Reference: VS Code Source Control

| Action | How to Do It |
|--------|--------------|
| **See changes** | Click Source Control icon (left sidebar) |
| **Stage files** | Click "+" next to file (or "+" at top for all) |
| **Commit** | Type message, click "✓ Commit" button |
| **Sync** | Click "Sync Changes" or ↻ icon (bottom left) |
| **Switch branch** | Click branch name (bottom left) → select branch |
| **Create branch** | Click branch name → "+ Create new branch" |

**Alternatively:** You can use GitHub Desktop for all Git operations if you prefer a visual interface. The workflow is the same (create branch → commit → sync → PR).

---

### Troubleshooting

**"I don't see the 'Sync Changes' button"**  
Look at the bottom left of VS Code for the ↻ sync icon. Click it to sync.

**"VS Code asks me to publish the branch"**  
Click "OK" or "Publish Branch". This is normal the first time you sync a new branch.

**"My changes don't show in Source Control"**  
Make sure you saved your files (Ctrl+S or Cmd+S). Then click the Source Control icon to refresh.

**"I'm on the wrong branch"**  
Click the branch name at the bottom left → select the branch you want (e.g., `phase-1`).

**"How do I see what I changed?"**  
Click Source Control icon. Each file shows what changed (red = removed, green = added). Click a file to see the diff.

**"I prefer a visual Git tool"**  
Use GitHub Desktop instead. The workflow is the same, just with buttons instead of VS Code's Source Control panel.
