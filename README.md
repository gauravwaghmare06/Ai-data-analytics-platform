# AI Data Analytics Platform

AI Data Analytics Platform is a production-focused portfolio project for dataset upload, profiling, and progressively expanding analytics capabilities.

## Phase 2 Status (Current)

✅ **Completed:** Dataset Upload & Data Profiling

Implemented through Phase 2:
- Modular Streamlit application foundation
- Centralized environment-based configuration
- Reusable logging and exception hierarchy
- File validation utilities for upload type/size checks
- CSV/XLSX dataset loading service with robust error handling
- Reusable data profiling service for overview, quality, numeric, and categorical summaries
- Session-state dataset management for active uploaded data
- Data Profiling UI page with:
  - upload section
  - KPI summary cards
  - dataset preview
  - column information table
  - data-quality warnings
  - numeric and categorical summaries
- Pytest coverage for configuration, validators, loader, profiler, and exceptions

Not implemented yet (planned later):
- Data cleaning workflow
- Advanced dashboarding/visual storytelling
- AI insights and natural-language dataset Q&A
- Machine learning prediction pipelines

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
│  │  └─ data_profile.py
│  ├─ services/
│  │  ├─ data_loader.py
│  │  ├─ data_profiler.py
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
4. Review dataset summary KPIs (rows, columns, missing values, duplicates).
5. Inspect preview, column-level profile, quality warnings, and statistical summaries.

You can use `data/sample/sales_demo.csv` as a safe synthetic demo dataset.

## Run Tests

```bash
pytest -q
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
- **Phase 3 (Planned):** Data cleaning and expanded EDA capabilities
- **Phase 4 (Planned):** Advanced visualization and export enhancements
- **Phase 5 (Planned):** AI insights, Q&A, and ML capabilities

## Architecture Reference

- `docs/architecture-and-development-plan.md`
