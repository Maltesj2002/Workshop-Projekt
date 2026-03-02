# Instructor Setup: GitHub Desktop Workflow

This guide explains how to set up and manage the GitHub Desktop + VS Code workflow for phased development submission.

## Overview

**Student workflow:**

1. Clone repo with GitHub Desktop
2. Create branch `phase-1` in GitHub Desktop
3. Edit code in VS Code
4. Commit & sync in GitHub Desktop
5. Create PR on GitHub.com
6. You review → approve/request changes
7. Repeat for Phase 2, 3, etc.

**Your workflow:**

1. Receive PR notifications
2. Run validation scripts
3. Review code
4. Approve or request changes
5. Merge when ready

---

## Pre-Class Setup (First Time Only)

### 1. Create a GitHub Organization or Use Your Account

If you don't have one already:

- Go to GitHub.com
- Create an organization for your class (or use your personal account)
- Create a REPOSITORY from this template

### 2. Give Students Access

```bash
# Add students as collaborators or members:
# Settings → Collaborators → Add each student
# (Or Settings → Teams if using organization)
```

### 3. Share Repository Link with Students

Send students:
```
GitHub repository URL: https://github.com/[your-org]/simulated-city-[class]
Download GitHub Desktop: https://desktop.github.com/
```

---

## Student Initial Setup (Day 1)

### Students need to:

1. **Install GitHub Desktop** (if not already installed)
   - Download from [https://desktop.github.com/](https://desktop.github.com/)
   - Sign in with their GitHub account

2. **Clone the repository**
   - Open GitHub Desktop
   - File → Clone Repository
   - Search for your repo name
   - Save to a local folder

3. **Open in VS Code**
   - In GitHub Desktop, click "Open in Visual Studio Code"
   - OR: In VS Code, File → Open Folder → select the cloned folder

---

## Phase Submission Workflow

### When Student Finishes Phase 1:

#### They do:

1. Create branch `phase-1` in GitHub Desktop (Current Branch → New Branch)
2. Implement Phase 1 in VS Code
3. Run validation:
   ```bash
   python scripts/verify_setup.py
   python scripts/validate_structure.py
   python -m pytest
   ```
4. Commit in GitHub Desktop: "Phase 1: Basic agent with MQTT"
5. Sync (Publish branch or Push origin)
6. Go to GitHub.com, create Pull Request
7. Fill in PR description (checklist of what was done)
8. Click "Create pull request"

#### You do:

1. **Notification step:** GitHub sends you an email about the new PR
2. **Review step:**
   ```bash
   # Clone the branch locally to test
   git fetch origin
   git checkout phase-1
   
   # Run validation
   python scripts/verify_setup.py
   python scripts/validate_structure.py
   python -m pytest
   
   # Run the notebook manually
   python -m jupyterlab
   ```
3. **Decision step:** On GitHub.com, either:
   - Click "Approve" (if it's good) → Merge the PR → Tell student to start Phase 2
   - Click "Request changes" (if fixes needed) → Student fixes → Push again → Re-review

---

## Managing Multiple Phases

### For Phase 2, 3, etc.:

Each phase gets its own branch:
- Phase 1: `phase-1` branch
- Phase 2: `phase-2` branch
- Phase 3: `phase-3` branch
- etc.

Each branch is independent. Students create a new branch for each phase:

```
In GitHub Desktop:
1. Go back to Main (Current Branch dropdown)
2. Click "New Branch"
3. Name it: phase-2
4. Based on: main (or latest)
5. Implement Phase 2
6. Commit & sync
7. Create PR from phase-2 branch
```

**Why separate branches?** If there's confusion or need to rollback, each phase is isolated.

---

## Code Review Checklist

When reviewing each PR, verify:

```bash
# Clone the branch
git fetch origin
git checkout phase-N

# Check environment
python scripts/verify_setup.py

# Check code structure (catches monolithic notebooks, folium, etc.)
python scripts/validate_structure.py

# Run tests
python -m pytest

# Manually test notebook (key step!)
python -m jupyterlab
# Open notebook, run all cells, verify it works
```

**In GitHub PR review:**

- [ ] Structure valid (no monolithic notebooks)
- [ ] No forbidden imports (folium, etc.)
- [ ] Dependencies in pyproject.toml (not !pip install)
- [ ] Only the stated phase implemented (no Phase 2 snuck in)
- [ ] Notebook runs without errors
- [ ] Student can explain what they built

---

## Common Scenarios

### Scenario 1: Phase 1 PR is Approved

On GitHub.com:

1. Click "Approve" button in the PR review
2. Click "Merge pull request" button
3. Confirm: "Confirm merge"
4. The phase-1 branch code is now in main ✅
5. Leave a comment: "Phase 1 approved! Merged. Pull the updated main branch and create `phase-2` to start Phase 2."

Student then:

1. Switches to `main` branch in VS Code (click branch name bottom left)
2. Syncs to pull the updated main (↻ icon)
3. Creates new branch `phase-2` from updated main
4. Implements Phase 2
5. Submits Phase 2 PR
6. You review again

**Key:** Each phase builds on the previous approved phase because main is updated after each merge.

### Scenario 2: Phase 1 PR Needs Changes

On GitHub.com:

1. Click "Request changes" button
2. Leave a comment: "The notebook has 500 cells. Split it into separate agent notebooks. See docs/exercises.md for examples."
3. Close the PR (don't merge)

Student then:

1. Continues working on `phase-1` branch in VS Code
2. Makes fixes
3. Commits & syncs again
4. The PR updates automatically with new commits
5. You re-review

### Scenario 3: Student Forgot to Run Validation

You run validation and find issues:
```bash
python scripts/validate_structure.py
# Output: ⚠️ notebooks/agent_transport.ipynb has 500 cells (max 300)
```

Comment on the PR:
> "Validation error: Notebook has 500 cells, max is 300. Split it into separate notebooks (one agent per notebook). Run `python scripts/validate_structure.py` locally before submitting next time."

---

## Tips & Tricks

### 1. Automate Validation (Optional)

If using GitHub Actions, you can run validation automatically on every PR:

```bash
# Create: .github/workflows/validate.yml
mkdir -p .github/workflows
cat > .github/workflows/validate.yml << 'EOF'
name: Validate Code Structure

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: python scripts/validate_structure.py
      - run: pip install -e ".[dev,notebooks]"
      - run: python -m pytest
EOF
```

Then GitHub will automatically run validation on each PR (even without you manually running it).

### 2. Use GitHub Protected Branches

To require review before merge:

1. Settings → Branches
2. "Add rule" on `main` branch
3. Require 1 approval before merge
4. This forces: PR → Review → Approval → Merge

### 3. Comment Templates

Create response templates for common feedback:

```markdown
## ❌ Monolithic Notebook
The notebook has [X] cells. Max is 300. Split into:
- notebooks/agent_transport.ipynb
- notebooks/agent_environment.ipynb
- notebooks/dashboard.ipynb

See docs/exercises.md for examples.

### ❌ Using Folium
Use anymap-ts instead. See .github/copilot-instructions.md for rules.

### ✅ Phase 1 Approved!
Great work. Ready for Phase 2. Create a new branch `phase-2` and implement Phase 2 from your approved plan.
```

---

## Troubleshooting

**Q: Student says "My branch is behind main"**  
A: In GitHub Desktop: Fetch origin → Rebase → Push origin  
   (Or simpler: delete the branch, create new one from latest main)

**Q: Student created Phase 2 branch but started implementing on Phase 1**  
A: Have them switch to phase-2 branch in GitHub Desktop and commit there instead.

**Q: I accidentally merged Phase 1 but student isn't done yet**  
A: No problem. The work is merged. Student creates Phase 2 branch from main and continues.

**Q: Student's notebook still has errors after they pushed**  
A: Comment on PR: "I ran the notebook and got this error: [error]. Please fix and push again."

---

## That's It!

The workflow is simple:

1. Student: code → commit → sync → PR
2. You: review → approve/request changes → merge
3. Repeat for next phase

The validation scripts catch bad architecture automatically, so you mainly just need to verify they only implemented ONE phase.
