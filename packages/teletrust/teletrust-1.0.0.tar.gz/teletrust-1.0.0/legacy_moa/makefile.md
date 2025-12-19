# Magnetic Outlier Agent – Development Guide

## 1️⃣ Create a virtual environment (if it doesn’t exist)

```powershell
python -m venv .venv
```

## 2️⃣ Upgrade pip and install the package in editable mode (+ optional dev extras)

```powershell
.\.venv\Scripts\pip install --upgrade pip
.\.venv\Scripts\pip install -e .[dev]   # add any extras you need in pyproject.toml
```

## 3️⃣ Run the CLI entry‑point

```powershell
.\.venv\Scripts\python -m magnetic_outlier_agent.cli.main  # add any CLI args after this
```

## 4️⃣ Run the test suite (requires pytest)

```powershell
.\.venv\Scripts\pytest tests
```

## 5️⃣ Build a wheel & sdist (requires the `build` package)

```powershell
.\.venv\Scripts\python -m build
```

## 6️⃣ Clean up generated artefacts

```powershell
if (Test-Path .venv) { Remove-Item -Recurse -Force .venv }
if (Test-Path build) { Remove-Item -Recurse -Force build }
if (Test-Path dist) { Remove-Item -Recurse -Force dist }
if (Test-Path *.egg-info) { Remove-Item -Recurse -Force *.egg-info }
```
