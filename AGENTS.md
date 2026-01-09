# Repository Guidelines

## Project Structure & Module Organization
- `main.py` provides the interactive menu for generation and validation.
- `generates/` contains generation scripts (`generate_n1.py`, `generate_n2.py`, `generate_n3.py`, `generate_n1n2.py`, `generate_n1n2n3.py`) and the menu.
- `validates/` contains validation scripts (`validate_n1.py`, `validate_n2.py`, `validate_n3.py`, `validate_n1n2.py`, `validate_n1n2n3.py`) and the menu.
- `utils/` houses shared helpers (generation, validation, logging, screen UI).
- `prompts/` stores prompt templates for N1/N2/N3.
- `dataset.json` is the input text dataset.
- `predicts/` stores generated outputs.
- `metrics/` stores validation outputs.
- `docs/` stores images and badges.
- `test.py` runs a small N1->N2->N3 pipeline on the first dataset item and writes `predicts/generate_test.py`.

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
python generates/generate_n1.py --model mistral
python generates/generate_n2.py --model mistral
python generates/generate_n3.py --model mistral
python generates/generate_n1n2n3.py --model mistral
```
Run validation scripts:
```bash
python validates/validate_n1.py
python validates/validate_n2.py
python validates/validate_n3.py
python validates/validate_n1n2n3.py
```
Run a small pipeline sample:
```bash
python test.py
```

## Coding Style & Naming Conventions
- Python files use 4-space indentation; keep code readable and minimal.
- Follow existing naming patterns: `snake_case` for functions/variables, concise script names (e.g., `generate_n1.py`).
- No formatter or linter is configured; avoid large style-only diffs.

## Testing Guidelines
- No automated test runner is set up. Validate changes by running the relevant scripts and checking generated JSON in `predicts/` or outputs in `metrics/`.

## Commit & Pull Request Guidelines
- Commit messages in history are short, title-style summaries (e.g., `Generate N1`, `Readme`, `Models`). Keep them concise and task-focused.
- PRs should describe what changed, how to reproduce (commands), and link any relevant data/artifacts. Include screenshots only when updating docs/plots.

## Configuration Notes
- External dependencies include `ollama` and CUDA Toolkit 11.8 for GPU workflows.
- Use a virtual environment (`venv` or `conda`) to isolate Python dependencies.
