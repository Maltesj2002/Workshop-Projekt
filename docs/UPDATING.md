# Updating Documentation Files

If your instructor announces that documentation files have been updated, use these commands to download the latest versions.

**Template Repository:** https://github.com/Esbern/simulated-city-template

**Your instructor's username:** Ask your instructor if they forked the template to their own account. If yes, use their username. If no, use `Esbern` (the original template author).

## macOS / Linux / Git Bash (Windows)

```bash
# Navigate to the docs directory
cd docs

# If your instructor forked the template (use their GitHub username):
curl -O https://raw.githubusercontent.com/INSTRUCTOR-USERNAME/simulated-city-template/main/docs/STUDENT_GUIDE.md
curl -O https://raw.githubusercontent.com/INSTRUCTOR-USERNAME/simulated-city-template/main/docs/PROMPT_TEMPLATES.md

# OR if using the original Esbern template:
curl -O https://raw.githubusercontent.com/Esbern/simulated-city-template/main/docs/STUDENT_GUIDE.md
curl -O https://raw.githubusercontent.com/Esbern/simulated-city-template/main/docs/PROMPT_TEMPLATES.md

# Optional: Update copilot instructions if instructor changed requirements
cd ..
curl -O https://raw.githubusercontent.com/Esbern/simulated-city-template/main/.github/copilot-instructions.md
# (or use INSTRUCTOR-USERNAME instead of Esbern if forked)

# Return to repository root
cd ..
```

## Windows PowerShell

```powershell
# Navigate to the docs directory
cd docs

# If your instructor forked the template (use their GitHub username):
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/INSTRUCTOR-USERNAME/simulated-city-template/main/docs/STUDENT_GUIDE.md" -OutFile "STUDENT_GUIDE.md"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/INSTRUCTOR-USERNAME/simulated-city-template/main/docs/PROMPT_TEMPLATES.md" -OutFile "PROMPT_TEMPLATES.md"

# OR if using the original Esbern template:
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Esbern/simulated-city-template/main/docs/STUDENT_GUIDE.md" -OutFile "STUDENT_GUIDE.md"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Esbern/simulated-city-template/main/docs/PROMPT_TEMPLATES.md" -OutFile "PROMPT_TEMPLATES.md"

# Optional: Update copilot instructions if instructor changed requirements
cd ..
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Esbern/simulated-city-template/main/.github/copilot-instructions.md" -OutFile "copilot-instructions.md"
# (or use INSTRUCTOR-USERNAME instead of Esbern if forked)

# Return to repository root
cd ..
```

## Commit the Updates (Optional)

After downloading, you can commit the updated files:

```bash
git add docs/STUDENT_GUIDE.md docs/PROMPT_TEMPLATES.md
git commit -m "Update documentation guides from instructor"
git push
```

## What Files Are Safe to Update This Way?

✅ **Safe to overwrite (instructor-maintained guides):**
- `docs/STUDENT_GUIDE.md`
- `docs/PROMPT_TEMPLATES.md`
- `docs/exercises.md`
- `.github/copilot-instructions.md`

❌ **Do NOT overwrite (your work):**
- `docs/concepts.md` — Your design clarification
- `docs/implementationplan.md` — Your phased plan
- `docs/phase_*_runtime.md` — Your runtime documentation
- `README.md` — Your project description
- `config.yaml` — Your configuration
- `notebooks/*.ipynb` — Your notebooks
- `src/simulated_city/*.py` — Your code

## Troubleshooting

**"Command not found: curl"**  
Try PowerShell commands instead, or download manually from GitHub web interface.

**"Failed to connect"**  
Check that you replaced `INSTRUCTOR-USERNAME` with the correct GitHub username (or used `Esbern` for the original template).

**"File not found (404)"**  
Verify the instructor's GitHub username and that the file exists at that location. Ask your instructor for the correct URL or username.
