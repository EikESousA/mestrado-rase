# Repository Guidelines

## Project Structure & Module Organization
- `src/` holds the main codebase.
  - `src/functions/` contains generation scripts (e.g., `generate_n1.py`, `generate_n2.py`).
  - `src/databases/` stores input/output JSON datasets.
  - `src/metrics/` contains evaluation examples and notebooks.
  - `src/utils/` and `src/helpers/` provide supporting scripts and reference files.
  - `src/models/` is reserved for model artifacts (tracked via `.gitkeep`).
- `src/train/` includes LoRA training utilities with its own `README.md`.
- `docs/` stores images and badges; `article/` holds the thesis document.

## Build, Test, and Development Commands
Install dependencies (Python 3.11.9 recommended):
```bash
pip install -r requirements.txt
```
Train dependencies live in `src/train/requirements.txt`:
```bash
pip install -r src/train/requirements.txt
```
Run generation scripts:
```bash
python src/functions/generate_n1.py
python src/functions/generate_n2.py
```
Train LoRA models (see `src/train/README.md` for model options):
```bash
python src/train/download_and_convert.py
python src/train/train_lora.py mistral
```
Run inference checks:
```bash
python src/train/test_infer.py mistral
```

## Coding Style & Naming Conventions
- Python files use 4-space indentation; keep code readable and minimal.
- Follow existing naming patterns: `snake_case` for functions/variables, concise script names (e.g., `generate_n1.py`).
- No formatter or linter is configured; avoid large style-only diffs.

## Testing Guidelines
- No automated test runner is set up. Validate changes by running the relevant scripts and checking generated JSON in `src/databases/` or outputs in `src/metrics/`.
- Notebooks in `src/utils/` are used for exploratory checks; keep outputs trimmed before committing.

## Commit & Pull Request Guidelines
- Commit messages in history are short, title-style summaries (e.g., `Generate N1`, `Readme`, `Models`). Keep them concise and task-focused.
- PRs should describe what changed, how to reproduce (commands), and link any relevant data/artifacts. Include screenshots only when updating docs/plots.

## Configuration Notes
- External dependencies include `ollama` and CUDA Toolkit 11.8 for GPU workflows.
- Use a virtual environment (`venv` or `conda`) to isolate Python dependencies.
