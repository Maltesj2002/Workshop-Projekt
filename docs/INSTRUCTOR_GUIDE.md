# Instructor's Guide: Document-Driven Development Workshop

This guide explains the pedagogy and how to enforce the methodology with students, even when models change.

## The Methodology: Document-Driven AI Development

### What We're Teaching

Students are learning:

1. **AI as a tool for thought clarification** — Not just code generation
2. **Structured prompting** — How to ask AI the right questions in the right order
3. **Validation and skepticism** — Don't trust AI output; verify it locally
4. **Distributed systems** — MQTT-based agent communication (real architecture, not toy code)
5. **Architecture through documentation** — Design first, code second

### Why This Matters

Too many students use AI to:

- Jump straight to implementation without understanding the problem
- Generate monolithic code that "works" but isn't maintainable
- Copy-paste packages (like `folium`) without considering integration
- Miss the opportunity to think through system design

This workshop flips the script: **Documentation is the deliverable. Code is the proof.**

---

## Enforcing the Workflow

### Phase 1: Design Clarification (Days 1-2)

**What students do:**

1. Fill in the 4-component template in README
2. Prompt AI with Phase 1 prompt from README.md (clarify, don't code)
3. Iterate with AI until the design is clear
4. Save the clarified design in the README or PR description

**How to verify:**

```bash
# Check they filled in README
git diff README.md | grep -i "trigger\|observer\|control\|response"

# Check for code in their first PR
git log --oneline | head -1
# Should NOT have any .ipynb files yet
```

**Common mistake:** Student jumps to coding.  
**Your response:**  
> "No code yet. Use the Phase 1 prompt from README.md — clarify the design first. Document the 4 components, the MQTT topics, and configuration parameters. Once I approve the design, we'll ask for an implementation plan."

---

### Phase 2: Implementation Planning (Day 2-3)

**What students do:**

1. Use Phase 2 prompt to ask AI for an implementation plan
2. AI proposes 5-6 phases, each implementing one concept
3. Student reviews and approves the plan

**How to verify:**

```bash
# PR should show the plan (in description or as a doc)
# Should NOT contain extensive code yet
# Should have clear phase descriptions
```

**Red flags:**

- Plan is vague ("implement everything")
- Plan suggests implementing 5 phases at once
- Plan doesn't match the design from Phase 1

**Your response:**  
> "The plan looks good. Now implement ONLY Phase 1. Test it, understand it, then we'll move to Phase 2."

---

### Phase 3: Phased Implementation (Week 1-2)

**What students do:**

1. Implement Phase 1 only
2. Test: `python scripts/verify_setup.py && python -m pytest`
3. Validate structure: `python scripts/validate_structure.py`
4. Run the notebook manually and explain what it does
5. **Submit Phase 1** (via Git PR if using GitHub, or folder snapshot if not)
6. Once approved, ask for Phase 2 implementation

**How to verify:**

```bash
# After each phase submission, run:
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest

# Check the notebook doesn't violate rules:
# - Doesn't exceed 300 cells
# - Doesn't use folium/matplotlib/plotly for real-time maps
# - Uses anymap-ts for any mapping
# - Uses mqtt.connect_mqtt() if it's an agent
```

**Review checklist:**

- [ ] Does this submission implement ONLY the approved phase?
- [ ] Did the student run validation scripts?
- [ ] Does the code follow `.github/copilot-instructions.md`?
- [ ] Can the student explain what the code does?
- [ ] Are dependencies in pyproject.toml (not !pip install)?
- [ ] Is the notebook size reasonable (<300 cells)?

**Common violation: Monolithic notebook**  

```bash
python -c "import json; nb = json.load(open('notebooks/agent_transport.ipynb')); print(f'Cells: {len(nb[\"cells\"])}')"
```
If > 300 cells, ask student to split it.

**Common violation: Using folium** 

```bash
grep -r "folium" notebooks/
```
If found, ask them to use `anymap-ts` instead.

---

### Optional: Using GitHub Pull Requests

**What:** A Pull Request (PR) is a GitHub feature that enforces code review workflow. Students submit code, you review, you approve before they move to the next phase.

**Tools:** GitHub Desktop + VS Code (no terminal commands needed)

- Students edit code in VS Code
- Students commit/sync using GitHub Desktop GUI
- Students create PR on GitHub.com
- You review PR on GitHub.com

**Pros:**

- Enforces phase-gating (can't skip phases)
- Creates a review trail (you can see what was built and when)
- Visual (GUI-based, no command line needed)
- Clean separation of work (one branch per phase)

**Cons:**

- Requires GitHub account setup (extra account per student)
- Adds workflow overhead (but minimal with GUI)

**Is it required?** No. You can use alternatives:

| Approach | When to Use |
|----------|------------|
| **GitHub PRs** | Class already uses Git; you want automatic enforcement |
| **Folder snapshots** | Simple alternative: student submits a `phase-1/` folder, you review it |
| **Shared document** | Document each phase's progress in a Google Doc or shared spreadsheet |
| **In-person review** | You meet with student, they show you the code running, you approve |

**If using PRs:** See [STUDENT_GUIDE.md](../STUDENT_GUIDE.md) "Submitting Your Work (Pull Requests)" section.

**If using folder snapshots:**

```bash
# After Phase 1, student submits:
phase-1/
├── notebooks/
│   └── agent_transport.ipynb
├── config.yaml
└── PHASE_1_NOTES.md  # What they learned

```
Then you verify with:
```bash

python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```

**Bottom line:** The **methodology** (document-driven, phased development) is what matters. PRs are one way to enforce it, but not the only way.

---

## Handling Model Changes

### Scenario: Your school switches from ChatGPT to Claude

**Good news:** The workflow is model-agnostic. Just provide students with:

1. The updated Phase 1 prompt (they copy-paste it)
2. The updated Phase 2 prompt
3. Phase 3 implementation prompt with embedded rules

**The validation tools do the heavy lifting:**

- `python scripts/verify_setup.py` — Catches dependency mistakes
- `python scripts/validate_structure.py` — Catches structural violations
- `python -m pytest` — Worst-case scenario detection

If different models produce different outputs, the **validation scripts catch violations before submission**.

### Scenario: Auto model selection (model changes per student/time)

No problem. The workflow handles this because:

1. Each prompt is self-contained with full rules
2. Validation is local and deterministic
3. You (the instructor) review before approving phases

The prompt templates include:
```
Remember these rules (from .github/copilot-instructions.md):
- Use anymap-ts for mapping (NOT folium)
- Each notebook is ONE agent (NOT monolithic)
...
```

This works with any model because **the constraints are explicit**.

---

## Teaching the "Rejection" Skill

A key skill: **rejecting AI output politely and specifically**.

### Teaching students to say "no":

Show them [STUDENT_GUIDE.md](STUDENT_GUIDE.md) section "Common AI Mistakes".

Examples:

- ❌ "This doesn't work" 
- ✅ "This uses folium, but we use anymap-ts. Rewrite it using anymap-ts from simulated_city."

- ❌ "Make it better"
- ✅ "Implement ONLY Phase 1. We'll do Phase 2 after testing Phase 1."

- ❌ "Fix the code"
- ✅ "The notebook has 500 cells. Split it into separate agent notebooks, one per agent. Each notebook publishes to a unique MQTT topic."

**Assignment:** Have students write a "rejection prompt" for each common mistake.

---

## Assessment Rubric

### Evaluate on:

**1. Adherence to Methodology (40%)**

- Did they document before coding?
- Did they get an approved plan?
- Did they implement phases sequentially?
- PR descriptions mention phases?

**2. Code Quality (30%)**

- Passes `python scripts/validate_structure.py`
- Passes `python -m pytest`
- Uses `anymap-ts` (not forbidden tools)
- Separate notebooks (not monolithic)
- Proper MQTT architecture

**3. Documentation (20%)**

- README filled with 4-component template
- Design clarification saved/documented
- Implementation plan documented
- Each notebook has clear comments

**4. Student Explanation (10%)**

- Can explain what their code does
- Can identify which phase is being implemented
- Can explain why they made architectural choices

---

## Common Issues and Solutions

### Problem: Student creates one big notebook with all agents

**Root cause:** AI suggested it, or student skipped the phase planning.

**Solution:**
```bash
# Detect monolithic notebook
python scripts/validate_structure.py

# Feedback:
> "This is a monolithic notebook. Split it into:
> - notebooks/agent_transport.ipynb (publishes traffic)
> - notebooks/agent_environment.ipynb (publishes air quality)
> - notebooks/dashboard.ipynb (subscribes to both)
> 
> Each notebook is one agent. They communicate via MQTT topics."
```

### Problem: Student installs folium instead of using anymap-ts

**Root cause:** AI suggested it, or they found a tutorial.

**Solution:**
```bash
# Detect folium
grep -r "folium" notebooks/

# Feedback:
> "Remove folium. Use anymap-ts instead:
> ```python
> from anymap_ts.jupyter import IPythonDisplay
> map_display = IPythonDisplay(center=[51.5, -0.1], zoom=12)
> ```
> See docs/exercises.md for examples."
```

### Problem: Student asks for all 5 phases at once

**Root cause:** Impatience or AI suggested it.

**Solution:**
> "We implement one phase at a time so you learn each part. 
> Test Phase 1, understand it, then ask for Phase 2.
> This is the whole point of document-driven development:
> small steps, deep understanding."

---

## Resources to Share with Students

1. **[README.md](README.md)** — Full workflow in 3 phases
2. **[STUDENT_GUIDE.md](STUDENT_GUIDE.md)** — Quick reference + common mistakes
3. **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — Rules they paste into every prompt
4. **[docs/exercises.md](docs/exercises.md)** — Concrete examples of proper structure
5. **[docs/setup.md](docs/setup.md)** — Environment validation

### Sample Rubric Text for Syllabus

> **Assessment:** Students are graded on:

> - Following the document-driven development workflow (clarify → plan → implement phases)
> - Code passing automated validation (`validate_structure.py`)
> - Ability to explain architectural choices and which phase is implemented
> - PRs that show sequential, phased development (not all-at-once implementation)

---

## Teaching Tips

### Make Documentation "Sacred"

- Have students share their README and approved design before any code
- Make code reviews focus on "Does this match the approved design?"
- Reward good documentation as much as working code

### Celebrate Rejection

- Share examples of good "rejection prompts" in class
- Celebrate when students catch AI mistakes
- Frame it as skill-building, not failure

### Use Real-World Analogy

> "You wouldn't build a house by asking a contractor to 'build the house,' then being surprised it's not what you want. You'd give detailed plans, approve them, then have them build phase by phase. AI is the same."

### Make Validation Part of Workflow

```bash
# Students should run this before every commit:
python scripts/verify_setup.py && python scripts/validate_structure.py && python -m pytest
```

Make it a habit, not an afterthought.

---

## Distributing Documentation Updates to Students

As you refine the workshop, you may update `STUDENT_GUIDE.md` or `PROMPT_TEMPLATES.md` to clarify instructions or add examples.

### How to Share Updates

**Template Repository:** https://github.com/Esbern/simulated-city-template

If you **forked** the template to your own GitHub account, students will download updates from your fork.

If you use the **original template unchanged**, students download from `Esbern/simulated-city-template`.

#### Option A: You Forked the Template (Most Flexible)

Students download from your fork:
```bash
curl -O https://raw.githubusercontent.com/YOUR-GITHUB-USERNAME/simulated-city-template/main/docs/STUDENT_GUIDE.md
```

Tell students: **"Use your instructor username: [YOUR-GITHUB-USERNAME]"**

#### Option B: Using the Original Template

Students download from the original:
```bash
curl -O https://raw.githubusercontent.com/Esbern/simulated-city-template/main/docs/STUDENT_GUIDE.md
```

Tell students: **"Use the original template repository (Esbern)"**

### Workflow for Distributing Updates

1. **Decide your approach:**
   - **Forked:** Updates go to your fork at `github.com/YOUR-USERNAME/simulated-city-template`
   - **Original:** Tell students to download from `https://github.com/Esbern/simulated-city-template`

2. **Make changes** to STUDENT_GUIDE.md or PROMPT_TEMPLATES.md
3. **Commit and push** to the `main` branch (your fork or contribute to original)
4. **Announce to class**: 
   - If you forked: "I've updated the documentation. Download using your instructor username: [YOUR-USERNAME]"
   - If original: "I've updated the documentation. Download from the original template: https://github.com/Esbern/simulated-city-template"
5. **Provide the download commands** from [UPDATING.md](UPDATING.md)

### What Files Should Students Update This Way?

**Update via download:**
- `docs/STUDENT_GUIDE.md` — Workflow and instructions
- `docs/PROMPT_TEMPLATES.md` — AI prompts and templates
- `docs/exercises.md` — Example exercises (if you add more)
- `.github/copilot-instructions.md` — AI rules (if you change requirements)

**Do NOT overwrite (students create these):**
- `docs/concepts.md` — Student's design clarification
- `docs/implementationplan.md` — Student's phased plan
- `docs/phase_*_runtime.md` — Student's runtime documentation
- `README.md` — Student's project description
- `config.yaml` — Student's configuration
- Notebooks and code

### Best Practice

Create a class announcement template:

**If you forked the template:**
```
📢 Documentation Update Available

I've updated the workshop documentation guides with [brief description of changes].

Download the latest version:
Your instructor GitHub username: [YOUR-GITHUB-USERNAME]

Follow the instructions in docs/UPDATING.md or docs/STUDENT_GUIDE.md

This will update:
- STUDENT_GUIDE.md
- PROMPT_TEMPLATES.md

Your project files (concepts.md, notebooks, code) will not be affected.
```

**If using the original template:**
```
📢 Documentation Update Available

I've updated the workshop documentation guides with [brief description of changes].

Download the latest version from the original template repository:
https://github.com/Esbern/simulated-city-template

Follow the instructions in docs/UPDATING.md or docs/STUDENT_GUIDE.md

This will update:
- STUDENT_GUIDE.md
- PROMPT_TEMPLATES.md

Your project files (concepts.md, notebooks, code) will not be affected.
```

---

## Advanced: Teaching Students to Compare Models

Once students master the workflow, have them try:

1. Phase 1 clarification with Model A (e.g., Claude)
2. Phase 1 clarification with Model B (e.g., ChatGPT)
3. Compare the two clarifications

## Key insight:**

> Different models clarify differently. Your job is to synthesize the best parts and reject the bad parts. This teaches critical thinking about AI output.

---

## FAQ for Instructors

**Q: What if folium is actually better for our use case?**  
A: It's not, for live MQTT data. But if you disagree with the architectural constraints, update `.github/copilot-instructions.md` and `pyproject.toml`. The validation scripts will enforce your chosen standards.

**Q: Can students use different AI models?**  
A: Yes. The workflow is model-agnostic. As long as they follow the prompt templates and run validation scripts, any model works.

**Q: How do I prevent students from skipping the documentation phase?**  
A: Check the README and approved design before allowing any code. Use the PR template checklist. Publicly celebrate students who document well.

**Q: What if a student's notebook runs but `validate_structure.py` complains?**  
A: Fix the validation error before merging. The validation scripts enforce the standard, not the functionality.

**Q: How do I know if they're really learning or just copy-pasting from AI?**  
A: Ask them to explain:
> "Describe what each cell in your notebook does. Why is it separate from the next cell?"  
If they can explain it, they understand it.
