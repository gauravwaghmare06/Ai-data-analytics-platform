# AI Data Analytics Platform - Technical Architecture & Development Plan

## 1) Recommended Folder Structure

```text
ai-data-analytics-platform/
├─ app.py
├─ requirements.txt
├─ README.md
├─ .env.example
├─ src/
│  └─ ai_data_analytics/
│     ├─ __init__.py
│     ├─ config/
│     │  ├─ __init__.py
│     │  ├─ settings.py
│     │  └─ logging_config.py
│     ├─ ui/
│     │  ├─ __init__.py
│     │  ├─ streamlit_app.py
│     │  ├─ pages/
│     │  │  ├─ upload_page.py
│     │  │  ├─ profiling_page.py
│     │  │  ├─ cleaning_page.py
│     │  │  ├─ visualization_page.py
│     │  │  ├─ insights_page.py
│     │  │  ├─ qa_page.py
│     │  │  └─ ml_page.py
│     │  └─ components/
│     │     ├─ dataset_preview.py
│     │     ├─ metric_cards.py
│     │     └─ chart_builder.py
│     ├─ core/
│     │  ├─ __init__.py
│     │  ├─ schemas.py
│     │  ├─ exceptions.py
│     │  └─ constants.py
│     ├─ ingestion/
│     │  ├─ __init__.py
│     │  ├─ file_validator.py
│     │  └─ dataset_loader.py
│     ├─ profiling/
│     │  ├─ __init__.py
│     │  ├─ summary_stats.py
│     │  ├─ quality_checks.py
│     │  └─ correlation.py
│     ├─ cleaning/
│     │  ├─ __init__.py
│     │  ├─ missing_values.py
│     │  ├─ outliers.py
│     │  ├─ type_inference.py
│     │  └─ deduplication.py
│     ├─ eda/
│     │  ├─ __init__.py
│     │  ├─ univariate.py
│     │  ├─ bivariate.py
│     │  └─ segmentation.py
│     ├─ visualization/
│     │  ├─ __init__.py
│     │  ├─ plot_factory.py
│     │  └─ theme.py
│     ├─ insights/
│     │  ├─ __init__.py
│     │  ├─ rule_based.py
│     │  └─ ai_insights_service.py
│     ├─ qa/
│     │  ├─ __init__.py
│     │  ├─ query_router.py
│     │  ├─ dataframe_qa.py
│     │  └─ llm_qa_service.py
│     ├─ ml/
│     │  ├─ __init__.py
│     │  ├─ preprocessing.py
│     │  ├─ training.py
│     │  ├─ evaluation.py
│     │  └─ inference.py
│     ├─ services/
│     │  ├─ __init__.py
│     │  ├─ session_state_service.py
│     │  ├─ cache_service.py
│     │  └─ export_service.py
│     └─ utils/
│        ├─ __init__.py
│        ├─ io_utils.py
│        ├─ dataframe_utils.py
│        └─ time_utils.py
├─ tests/
│  ├─ conftest.py
│  ├─ unit/
│  ├─ integration/
│  └─ fixtures/
│     └─ datasets/
└─ scripts/
   └─ run_streamlit.sh
```

## 2) Folder and Important File Responsibilities

- `app.py`: Application entrypoint that starts Streamlit app bootstrapping.
- `src/ai_data_analytics/config/settings.py`: Environment-driven settings (limits, file size, feature toggles, API config).
- `src/ai_data_analytics/ui/`: Presentation layer only; no heavy business logic.
- `src/ai_data_analytics/core/schemas.py`: Data contracts (typed structures) shared across modules.
- `src/ai_data_analytics/core/exceptions.py`: Custom, centralized exception hierarchy.
- `src/ai_data_analytics/ingestion/`: File validation and loading for CSV/XLSX into DataFrames.
- `src/ai_data_analytics/profiling/`: Dataset diagnostics (shape, nulls, types, distributions, correlations).
- `src/ai_data_analytics/cleaning/`: Deterministic data cleaning transforms and recommendations.
- `src/ai_data_analytics/eda/`: EDA computations for trends and relationships.
- `src/ai_data_analytics/visualization/`: Plotly figure generation with reusable chart builders.
- `src/ai_data_analytics/insights/`: Rule-based and later LLM-based insight generation.
- `src/ai_data_analytics/qa/`: Dataset question-answering pipeline (rule/DataFrame now, LLM later).
- `src/ai_data_analytics/ml/`: ML preprocessing, model training, evaluation, and prediction workflows.
- `src/ai_data_analytics/services/`: Stateful and cross-cutting services (session/cache/export).
- `src/ai_data_analytics/utils/`: Generic helper utilities with no domain-specific side effects.
- `tests/`: Unit and integration tests with realistic fixture datasets.
- `.env.example`: Document required environment variables only (never real secrets).

## 3) Application Flow (Upload to Final Analysis)

1. **Upload & Validate**
   - User uploads CSV/XLSX.
   - `file_validator` enforces extension, size, schema sanity, and safe parsing rules.
2. **Load & Normalize**
   - `dataset_loader` reads to DataFrame, normalizes column names/types.
3. **Profile Dataset**
   - Profiling modules compute metadata, null heatmap inputs, type breakdown, statistics.
4. **Cleaning Recommendations + Actions**
   - Cleaning modules suggest and apply missing-value, outlier, type-fix, and dedup rules.
5. **EDA + Interactive Visuals**
   - EDA generates analysis structures.
   - Visualization module converts results to Plotly charts.
6. **Insights Generation**
   - Rule engine creates narrative insights from computed metrics.
   - Later optional LLM layer augments insights.
7. **Dataset Q&A**
   - Natural-language question routed to deterministic query handlers and later LLM fallback.
8. **ML Prediction Workflow**
   - User selects target, algorithm, and features.
   - Training/evaluation results and predictions are presented and exportable.
9. **Export**
   - Reports, cleaned datasets, charts, and model metrics exported as downloadable artifacts.

## 4) Core Modules to Implement

- **Ingestion**: secure file parsing, schema checks, typed load responses.
- **Profiling**: null analysis, descriptive stats, cardinality checks, correlations.
- **Cleaning**: reproducible transform pipeline and user-selectable operations.
- **EDA**: reusable analysis primitives for numerical/categorical/time data.
- **Visualization**: chart factory for histogram, box, scatter, bar, heatmap, line.
- **Insights**: rule-based textual insight generation using profiling/EDA metrics.
- **Q&A**: question parser + DataFrame query executor + future LLM connector.
- **ML**: preprocessing pipeline, baseline models, metrics, and inference service.
- **UI Orchestration**: page routing and controlled session state transitions.

## 5) Dependency List

Required now:
- `streamlit`
- `pandas`
- `numpy`
- `scikit-learn`
- `plotly`
- `openpyxl`
- `pytest`

Recommended small additions (optional but practical):
- `python-dotenv` (load local environment variables safely)
- `scipy` (robust statistical helpers for EDA/outliers)

## 6) Development Phases (Correct Order)

1. **Foundation Setup**
   - Project structure, config management, logging, exception model.
2. **Data Ingestion + Validation**
   - File upload constraints and safe DataFrame loading.
3. **Profiling Engine**
   - Core quality/stats outputs and profile UI page.
4. **Cleaning Engine**
   - Deterministic transformations and before/after audit view.
5. **EDA + Visualization**
   - Analysis primitives and interactive chart tooling.
6. **Insights Module (Rule-Based First)**
   - Reliable non-LLM insights from computed metrics.
7. **Dataset Q&A (Deterministic First, LLM Later)**
   - Controlled query scope and explainable answers.
8. **ML Training + Prediction**
   - Guided model pipeline with metrics and validation.
9. **Hardening & UX Polish**
   - Performance tuning, robust error UX, export flows, docs.

## 7) Testing Strategy

- **Unit tests** for each module function (validation, transforms, metrics, chart outputs).
- **Integration tests** for full flow (upload -> profile -> clean -> visualize -> insights).
- **Fixture-driven tests** using diverse CSV/XLSX samples (missing values, malformed types, large cardinality).
- **Regression tests** for previously fixed bugs in transformations and model outputs.
- **Negative tests** for invalid file types, oversized inputs, and malformed datasets.
- **UI smoke tests** for key Streamlit interactions and state transitions.

## 8) Security Considerations

- Strict upload allowlist (`.csv`, `.xlsx`) and size limits.
- Parse files with defensive error handling; reject corrupted/spoofed content.
- Never commit secrets; use environment variables and `.env.example` only.
- Validate and sanitize user-entered query inputs (especially future SQL/LLM layers).
- Isolate model/LLM provider keys via environment config and least privilege.
- Avoid arbitrary code execution paths for DataFrame queries.
- Keep dependency versions pinned and regularly patched.

## 9) Future Scalability Improvements

- Introduce service boundaries (API backend + async workers) beyond Streamlit-only mode.
- Add dataset storage abstraction (local now, object storage later).
- Cache expensive profiling/EDA computations with keyed invalidation.
- Add background jobs for long-running ML training.
- Add plugin architecture for custom analytics modules.
- Introduce SQL query engine and vector-aware retrieval for advanced Q&A.
- Add observability: structured logs, metrics, and trace IDs.
- Containerization and deployment pipeline (Docker + CI/CD checks).

---

This architecture keeps UI, business logic, processing, ML, and utilities cleanly separated, aligns with PEP 8 and type-hint/docstring-friendly design, and is intentionally structured for incremental production hardening.
