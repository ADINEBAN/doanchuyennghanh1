# Drowsiness Desktop App
python -m app.main

cd web-admin
npm.cmd run dev

Desktop application scaffold for a driver drowsiness warning system built with Python, PyQt6, OpenCV, MediaPipe, and Supabase.

The codebase follows a `single repo + modular monolith + hybrid feature-based` structure:

- `app/features/`: user-facing features such as auth, monitoring, history, statistics, and settings.
- `app/shared/`: shared config, state, database access, widgets, styles, and utility helpers.
- `app/ai/`: runtime model loading and prediction helpers.

Current scope is finalized as:

- `Desktop app`: for `DRIVER`
- `Web admin`: for `SUPER_ADMIN` and `COMPANY_ADMIN`

## Current Status

The repository currently contains:

- Project architecture documentation.
- Supabase PostgreSQL schema.
- Source code scaffold for the desktop application.
- Training and test skeletons for the AI pipeline.

## Suggested Setup

### Runtime App Environment

Use this environment for the desktop app, webcam, MediaPipe, local auth, history, and statistics.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `.env` with your Supabase credentials before using online authentication and persistence.

### AI Training Environment

TensorFlow is intentionally separated from the runtime app because it can conflict with MediaPipe on some Windows/Python setups.

```powershell
python -m venv .venv-train
.venv-train\Scripts\Activate.ps1
pip install -r requirements-train.txt
```

Expected dataset layout:

```text
ml/datasets/raw/
  normal/
  closed_eyes/
  yawning/
  drowsy/
```

Prepare, train, and evaluate:

```powershell
python ml/training/preprocess_dataset.py --input ml/datasets/raw --output ml/datasets/processed
python ml/training/train_model.py --dataset ml/datasets/processed --output ml/exported_models
python ml/training/evaluate_model.py --model ml/exported_models/drowsiness_model.keras --dataset ml/datasets/processed/test
```

## Run

```powershell
python -m app.main
```

## Dependency Strategy

- `requirements.txt`: desktop app runtime only.
- `requirements-train.txt`: training/inference dependencies for TensorFlow-based model work.
- Runtime app can still open and work without TensorFlow installed.

## Repository Layout

- `app/features/`: feature modules.
- `app/shared/`: shared app building blocks.
- `app/ai/`: runtime inference layer.
- `db/`: Supabase schema.
- `docs/`: design and architecture notes.
- `ml/`: dataset, training, and exported model folders.
- `tests/`: unit test skeletons.

## Supabase

- Setup guide: [docs/supabase_setup.md](docs/supabase_setup.md)
- Database schema: [db/supabase_schema.sql](db/supabase_schema.sql)
- Connection check:

```powershell
python scripts/verify_supabase_connection.py
```

## Next Implementation Targets

1. Replace local fallback authentication with real Supabase flows.
2. Connect dashboard camera loop to `webcam_manager`.
3. Stabilize MediaPipe runtime on the target demo machine.
4. Add real history/statistics queries against Supabase.
5. Train and integrate the first AI model in a separate training environment.
