# Repository Guidelines

## Project Structure & Module Organization

`data/allstate_claims_data.csv` is the supplied dataset; keep outputs separate from it. Group notebooks by milestone under `notebooks/` (for example, `notebooks/September/Gate 1/`). `notebooks/EDA-Design.md` records the exploration plan; `docs/coach/` contains event notes and milestones. See `Challenge-Project-Overview.md` for the problem definition and `README.md` for results. There is no application source tree or test directory yet.

## Development Commands

For local Jupyter, work from the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install jupyterlab
python -m jupyter lab notebooks
```

`requirements.txt` is currently empty; add and install packages your notebook imports. There is no build command. Run notebooks from top to bottom before sharing them.

## Google Colab and Drive Paths

For Colab only, upload or copy the repository (including `data/`) into your Google Drive, then run this cell before reading the CSV:

```python
from google.colab import drive
drive.mount("/content/drive")
```

Authorize access when prompted. Drive files then appear under `/content/drive/MyDrive/`. Set the path to **your** folder layout; the example notebook uses `MyDrive/Allstate 1A/Colab Allstate_1A/data/allstate_claims_data.csv`, which may differ on your Drive:

```python
from pathlib import Path
import pandas as pd
csv_path = Path("/content/drive/MyDrive/<your-folder>/data/allstate_claims_data.csv")
df = pd.read_csv(csv_path)
```

Replace `<your-folder>` and check `csv_path.exists()` before loading. Do not copy another contributor's personal Drive path unchanged.

## Coding Style & Naming Conventions

Use four spaces for Python indentation, `snake_case` for variables and notebook filenames, and descriptive Markdown headings. Explain each analysis near its code. Name notebooks by milestone and task, such as `notebooks/October/task_2_baseline.ipynb`. Keep generated reports, checkpoints, virtual environments, and derived datasets out of commits. No formatter or linter is configured; use PEP 8 style.

## Testing Guidelines

No test framework or coverage threshold is configured. For notebook changes, restart the kernel and run all cells; check outputs against the narrative. For models, report mean absolute error (MAE) on held-out data, fit preprocessing only on training data, and document the split and random seed. Add tests under `tests/` for reusable Python modules.

## Commit & Pull Request Guidelines

Recent commits use short subjects such as `task 1 notebook` and `docs: update next session date`; use an imperative summary and optional area prefix (`docs:`, `notebooks:`). In pull requests, describe the milestone, changes, dependency needs, and checks. Link the task or issue; include plots or screenshots when visual results change. Avoid committing personal paths or credentials.
