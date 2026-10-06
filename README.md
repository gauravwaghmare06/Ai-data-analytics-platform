# AI Data Analytics Platform

AI Data Analytics Platform is a production-focused portfolio project for dataset upload, profiling, cleaning, and progressively expanding analytics capabilities.

## Phase 3 Status (Current)

✅ **Completed:** Data Cleaning & Transformation

Implemented through Phase 3:
- Modular Streamlit foundation with clear UI/service separation
- CSV/XLSX dataset upload with validation and robust error handling
- Dataset profiling (overview, column metadata, quality checks, numeric/categorical summaries)
- Dedicated data-cleaning service with reusable operations:
  - missing-value handling (drop rows, mean, median, mode, custom value)
  - duplicate detection and removal
  - column rename/remove/normalize
  - data type conversion (numeric, string, datetime, boolean)
  - IQR outlier analysis with optional removal
  - safe row filtering (no `eval`)
- Session-state dataset lifecycle:
  - original dataset preserved
  - current cleaned dataset updated per operation
  - cleaning operation history tracked with timestamps
  - reset-to-original support
- Cleaned dataset export:
  - CSV download
  - Excel download
- Expanded pytest coverage for loader, profiler, cleaner, validators, and state behavior

Not implemented yet (planned later phases):
- Advanced dashboarding/visual storytelling
- AI insights and natural-language dataset Q&A
- Machine learning prediction pipelines
- Authentication and database-backed workflows

## Supported Data Formats

- `.csv`
- `.xlsx`

Upload limits and allowed extensions are controlled by environment variables.

## Technology Stack

- Python 3.12+
- Streamlit
- Pandas
- OpenPyXL
- python-dotenv
- pytest

## Project Structure

```text
ai-data-analytics-platform/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ pages/
│  │  ├─ data_profile.py
│  │  └─ data_cleaning.py
│  ├─ services/
│  │  ├─ data_loader.py
│  │  ├─ data_profiler.py
│  │  ├─ data_cleaner.py
│  │  └─ dataset_state.py
│  └─ utils/
│     ├─ exceptions.py
│     ├─ logger.py
│     └─ validators.py
├─ data/
│  └─ sample/
│     └─ sales_demo.csv
├─ docs/
├─ models/
├─ screenshots/
├─ tests/
├─ .env.example
├─ requirements.txt
└─ README.md
```

## Local Setup

```bash
git clone https://github.com/gauravwaghmare06/Ai-data-analytics-platform.git
cd Ai-data-analytics-platform
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell virtual environment activation:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## Run the Application

```bash
streamlit run app/main.py
```

## How to Use Data Profiling

1. Open the app.
2. Go to **Data Profiling** from the sidebar.
3. Upload a CSV or XLSX file.
4. Review KPIs, preview, column profile, quality warnings, and statistical summaries.

## How to Use Data Cleaning

1. Go to **Data Cleaning** from the sidebar.
2. Upload or reuse the active dataset.
3. Apply cleaning operations section by section.
4. Track applied operations in **Cleaning History**.
5. Use **Reset to Original Dataset** to recover the original uploaded data.
6. Export the current cleaned dataset as CSV or Excel.

You can use `data/sample/sales_demo.csv` as a safe synthetic demo dataset.

## Original vs Cleaned Dataset Behavior

- **Original dataset** is preserved in session state and never mutated by cleaning actions.
- **Current cleaned dataset** is updated after each operation.
- Reset restores the current cleaned dataset back to the original upload.

## Run Tests

```bash
python -m pytest -q
```

## Environment Variables

Defined in `.env.example`:
- `APP_NAME`
- `APP_ENV`
- `APP_DEBUG`
- `APP_LOG_LEVEL`
- `APP_MAX_UPLOAD_SIZE_MB`
- `APP_ALLOWED_UPLOAD_EXTENSIONS`

## Development Roadmap

- **Phase 1 (Completed):** Production foundation
- **Phase 2 (Completed):** Dataset upload and profiling
- **Phase 3 (Completed):** Data cleaning and transformation
- **Phase 4 (Planned):** Advanced visualization and export enhancements
- **Phase 5 (Planned):** AI insights, Q&A, and ML capabilities

## Architecture Reference

- `docs/architecture-and-development-plan.md`
