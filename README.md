# AI Data Analytics Platform

AI Data Analytics Platform is a production-focused portfolio project designed to provide a reliable foundation for dataset-driven analytics workflows that will evolve across structured development phases.

## Phase 1 Status (Current)

✅ **Completed:** Production Project Foundation

Implemented in Phase 1:
- Modular project structure for app, services, pages, utilities, tests, and data assets
- Streamlit entry point with professional landing shell and clean navigation
- Centralized environment-based configuration
- Reusable logging module
- Custom exception hierarchy
- Reusable validation utilities (file type, file size, required config values)
- Initial pytest suite for core foundation behavior
- Synthetic sample dataset for safe local development

Not implemented yet (planned for later phases):
- Data profiling and cleaning workflows
- EDA dashboards and interactive advanced visual analytics
- AI insights and dataset Q&A
- ML prediction pipelines

## Technology Stack

- Python 3.12+
- Streamlit
- python-dotenv
- pytest

## Project Structure

```text
ai-data-analytics-platform/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ components/
│  ├─ pages/
│  ├─ services/
│  └─ utils/
│     ├─ exceptions.py
│     ├─ logger.py
│     └─ validators.py
├─ data/
│  └─ sample/
├─ docs/
├─ models/
├─ screenshots/
├─ tests/
├─ .env.example
├─ requirements.txt
└─ README.md
```

## Local Setup

### 1) Clone repository

```bash
git clone https://github.com/gauravwaghmare06/Ai-data-analytics-platform.git
cd Ai-data-analytics-platform
```

### 2) Create and activate virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` as needed for your local environment.

## Run the Streamlit Application

```bash
streamlit run app/main.py
```

## Run Tests

```bash
pytest -q
```

## Environment Variable Setup

Defined in `.env.example`:
- `APP_NAME`
- `APP_ENV`
- `APP_DEBUG`
- `APP_LOG_LEVEL`
- `APP_MAX_UPLOAD_SIZE_MB`
- `APP_ALLOWED_UPLOAD_EXTENSIONS`
- `OPENAI_API_KEY` (placeholder only for future integration)

## Development Roadmap

- **Phase 1 (Completed):** Production project foundation
- **Phase 2:** Dataset ingestion and validation workflow integration
- **Phase 3:** Profiling, cleaning, and EDA modules
- **Phase 4:** Interactive visualization and export enhancements
- **Phase 5:** AI insights, Q&A, and ML capabilities

## Architecture Reference

See the approved architecture and phased plan:
- `docs/architecture-and-development-plan.md`
