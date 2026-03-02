# Pull Request

## Description
<!-- Explain what this PR does. -->

## Phases Completed
<!-- Which phases from the implementation plan are in this PR? -->
- [ ] Phase 1 (design clarification)
- [ ] Phase 2 (basic single agent)
- [ ] Phase 3 (configuration)
- [ ] Phase 4 (MQTT publishing)
- [ ] Phase 5 (second agent with subscription)
- [ ] Phase 6 (dashboard visualization)
- [ ] Other: _______

## Document-Driven Development Checklist

Before submitting, verify you followed the workflow in [README.md](README.md):

1. **Design Phase** ✅
   - [ ] Filled in the 4-component template in README
   - [ ] AI clarified the design with you (no disagreement)
   - [ ] You got an implementation plan and approved it

2. **Implementation Phase** ✅
   - [ ] You asked AI for ONE phase only
   - [ ] You understand the code before moving to next phase
   - [ ] Tests pass: `python scripts/verify_setup.py && python -m pytest`

3. **Code Quality** ✅
   - [ ] Code follows `.github/copilot-instructions.md`
   - [ ] If notebooks: separate agent notebooks with MQTT (not monolithic)
   - [ ] Uses `anymap-ts` for mapping (not `folium`)
   - [ ] Dependencies in `pyproject.toml` (not `!pip install`)
   - [ ] Ran validation: `python scripts/validate_structure.py`

4. **Documentation** ✅
   - [ ] Docs updated: yes/no
   - [ ] If yes: which docs? (e.g., `docs/mqtt.md`, `docs/exercises.md`)
   - [ ] If no: why not? (brief explanation)

## Testing
Run these before submitting:
```bash
python scripts/verify_setup.py    # Check dependencies
python scripts/validate_structure.py  # Check code structure
python -m pytest                      # Run tests
python -m jupyterlab                  # Test your notebooks manually
```

---
**Important:** This workshop teaches **document-driven AI development**. 
Each phase teaches one concept. Don't skip phases or let AI implement everything at once.
See [README.md](README.md) for the full workflow.

