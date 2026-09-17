# LPDG_RGMCET_MASTERCLASS

Public repository for LPDG_RGMCET_MASTERCLASS, to maintain and share the scripts with participants.

This project is a small end-to-end weather forecasting demo built on Snowflake + Snowpark ML:
fetch weather data → load it into Snowflake → engineer features → train a model → register and
version it in the Snowflake Model Registry → serve predictions on new data.

---

## Notebooks

All notebooks live in `SCH_LPDG_RGMCET_MASTERCLASS/notebooks/`. Run them in this order the first
time through.

### 1. `Weather_API_Exploration.ipynb`
- Explores the Open-Meteo Historical Weather API before any pipeline code is written.
- Reviews the raw JSON response structure and profiles a sample dataset (shape, dtypes, nulls).
- Decides which weather variables and schema to carry forward into ingestion.

### 2. `Snowflake_connector.ipynb`
- Stand-alone reference for connecting to Snowflake from a `.env` file — no hardcoded credentials.
- Builds connection parameters, opens a session, and verifies the account/role/warehouse/database context.
- Not part of the pipeline itself; a teaching notebook for the connection pattern reused everywhere else.

### 3. `Weather_Data_Ingestion.ipynb`
- Fetches historical weather data from Open-Meteo using the variables chosen during exploration.
- Transforms the JSON response into a DataFrame and adds metadata columns (location, load timestamp).
- Creates `TBL_WEATHER_DATA` in Snowflake and loads the dataset into it.

### 4. `Preprocessing._Training.ipynb`
- Loads `TBL_WEATHER_DATA`, cleans it (types, nulls, duplicates, drops constant station metadata), and sorts it by time.
- Engineers forecasting features: lagged temperature/sensor readings and hour-of-day — using only *past* values, since this is a forecasting task.
- Splits the data chronologically (never shuffled) and trains a `snowflake.ml.modeling.ensemble.RandomForestRegressor` to predict next-hour temperature.

### 5. `Registry_Inference.ipynb`
- Loads the trained model and registers it in the Snowflake Model Registry with real evaluation metrics (MAE, R²).
- Demonstrates versioning: each retrain registers the next version (V1, V2, …) without overwriting previous ones, and a version can be promoted to "default".
- Runs inference by loading a model version back out of the registry and predicting on new/unseen data, with plots showing prediction accuracy.

---

## Project Structure

```
LPDG_RGMCET_MASTERCLASS/
├── .env                                  # Your real Snowflake credentials (git-ignored, never commit)
├── .env.example                          # Template showing which variables .env needs
├── venv/                                 # Local virtual environment (not committed)
│
└── SCH_LPDG_RGMCET_MASTERCLASS/
    ├── requirements.txt                  # Python dependencies for this project
    │
    ├── notebooks/                        # Teaching notebooks, run top to bottom (see above)
    │   ├── Weather_API_Exploration.ipynb
    │   ├── Snowflake_connector.ipynb
    │   ├── Weather_Data_Ingestion.ipynb
    │   ├── Preprocessing._Training.ipynb
    │   └── Registry_Inference.ipynb
    │
    └── Snowpark/
        ├── data/
        │   └── test_data.csv             # Held-out test set saved by Preprocessing._Training.ipynb;
        │                                 # uploaded to the Snowflake table TBL_WEATHER_TEST_DATA and
        │                                 # not read directly by any pipeline after that
        │
        ├── procedures/                   # Same pipelines, as Snowflake stored procedures
        │   ├── Data_Preprocessing.sql        # BUILD_TRAINING_DATA(): features + train/test split
        │   ├── Model_training.sql            # TRAIN_MODEL(): train, evaluate, register
        │   ├── Model_Inference.sql           # RUN_INFERENCE(input_table, output_table): predict
        │   └── run.py                        # Registers all three procedures, then calls them in order
        │
        └── src/
            ├── config/
            │   ├── weather_config.py     # Location, date range, and API variables for ingestion
            │   └── model_config.py       # Model name, feature/target columns, train/test split, RF settings
            │
            ├── utils/                    # Single-purpose helper functions, no orchestration logic
            │   ├── snowflake_connection.py   # get_session(): reads .env, opens a Snowpark session
            │   ├── weather_api.py            # Calls the Open-Meteo API
            │   ├── weather_transformer.py    # Converts the API's JSON response into a DataFrame
            │   ├── snowflake_loader.py       # Writes a DataFrame into a Snowflake table
            │   ├── feature_engineering.py    # Cleans data, builds lag/hour features, time-based split
            │   ├── model_trainer.py          # Trains the RandomForestRegressor
            │   ├── model_evaluator.py        # Computes MAE/R2 on predictions
            │   └── model_registry.py         # Register, list, promote, and serve model versions
            │
            ├── pipelines/                 # Orchestration: each file exposes a single run(session)
            │   ├── weather_ingestion_pipeline.py     # Fetch -> transform -> load into Snowflake
            │   ├── model_registry_pipeline.py        # Build features -> train -> evaluate -> register
            │   └── model_inference_pipeline.py       # Load serving model -> predict on new data
            │
            └── models/
                └── temperature_model.joblib   # A trained model artifact, saved for inspection/reuse
```

**Why the split between `utils/` and `pipelines/`:** each file in `utils/` does exactly one thing
(fetch, transform, train, evaluate, register) and can be tested on its own. Each file in
`pipelines/` just calls those pieces in order — it has no logic of its own, so the pipeline itself
is easy to read top to bottom.

---

## How to Run This Manually

### 1. Create and activate a virtual environment
```powershell
cd "LPDG_RGMCET_MASTERCLASS"
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```powershell
pip install -r "SCH_LPDG_RGMCET_MASTERCLASS\requirements.txt"
```

### 3. Set up your Snowflake credentials
```powershell
Copy-Item .env.example .env
```
Open `.env` and fill in your real Snowflake account, user, password, role, warehouse, database,
and schema. Never commit this file — it's already in `.gitignore`.

### 4. Register the Jupyter kernel for this venv
```powershell
python -m ipykernel install --user --name lpdg-masterclass --display-name "Python (LPDG Masterclass venv)"
```
In VS Code, open each notebook and select **"Python (LPDG Masterclass venv)"** as the kernel
(top-right of the notebook). If multiple Python environments exist on your machine, this step
matters — the wrong kernel silently uses a different environment with different package versions.

### 5. Run the notebooks in order
1. `Weather_API_Exploration.ipynb`
2. `Weather_Data_Ingestion.ipynb` (creates `TBL_WEATHER_DATA` in Snowflake)
3. `Preprocessing._Training.ipynb` (trains the model, saves `temperature_model.joblib` and a local `test_data.csv`)
4. `Registry_Inference.ipynb` (uploads `test_data.csv` into the Snowflake table `TBL_WEATHER_TEST_DATA`,
   registers the model, and runs inference — everything after that upload step reads from this table,
   not the CSV)

`Snowflake_connector.ipynb` is a reference notebook and can be run independently at any time to
verify your `.env` and connection are working.

### 6. Run the pipelines directly (no notebooks)
The same logic as the notebooks is also available as plain Python or as Snowflake stored
procedures, for automation or CI — see "Running Each Pipeline Step by Step" below for the
exact commands.

---

## Running Each Pipeline Step by Step

All commands below assume you already completed steps 1–4 above (venv activated, dependencies
installed, `.env` filled in) and are running from:
```powershell
cd "SCH_LPDG_RGMCET_MASTERCLASS\Snowpark\src"
```

### Step 1 — Weather ingestion pipeline
Fetches historical weather data from Open-Meteo and loads it into `TBL_WEATHER_DATA` in
Snowflake. Run this first — every later step reads from this table. Location and date range
come from `config/weather_config.py` — edit that file to change them, not the pipeline code.
```powershell
python -c "from utils.snowflake_connection import get_session; from pipelines.weather_ingestion_pipeline import run; run(get_session('dev'))"
```

### Step 2 — Model registry pipeline
Builds features from `TBL_WEATHER_DATA`, trains a Random Forest, evaluates it, and registers it
in the Snowflake Model Registry as the next version (V1, V2, V3, …). Never overwrites a
previous version.
```powershell
python -c "from utils.snowflake_connection import get_session; from pipelines.model_registry_pipeline import run; print(run(get_session('dev')))"
```
To make the new version the one that actually serves predictions, promote it explicitly
(use the version name printed above):
```powershell
python -c "from utils.snowflake_connection import get_session; from utils.model_registry import get_registry, set_default_version; set_default_version(get_registry(get_session('dev')), 'WEATHER_TEMPERATURE_MODEL', 'V3')"
```

### Step 3 — Model inference pipeline
Loads the current default (or a named) model version from the registry and predicts on
`TBL_WEATHER_TEST_DATA`.
```powershell
python -c "from utils.snowflake_connection import get_session; from pipelines.model_inference_pipeline import run; run(get_session('dev')).show()"
```

### Running inference on your own new data
`run` takes a `table_name`, so you don't need to touch pipeline code to score different data —
just point it at any Snowflake table with the same columns as `TBL_WEATHER_TEST_DATA`
(`TIMESTAMP`, `TEMPERATURE`, and the lag/`HOUR` feature columns):
```powershell
python -c "from utils.snowflake_connection import get_session; from pipelines.model_inference_pipeline import run; run(get_session('dev'), table_name='MY_NEW_TABLE', n_rows=20).show()"
```
To serve a specific model version instead of whatever is currently default, pass `version_name`
too: `run(session, version_name="V2", table_name="MY_NEW_TABLE")`.

Your new table needs the same lag columns as `TBL_WEATHER_TEST_DATA` (`TEMPERATURE_LAG_1`,
`HUMIDITY_LAG_1`, etc.) already computed, since this pipeline predicts directly on what you give
it rather than rebuilding features. If your new data is raw, engineer it first with
`utils/feature_engineering.py`'s `build_features()`.

### Alternative: run everything as Snowflake stored procedures
The same three steps are also available as SQL stored procedures in `Snowpark/procedures/`,
registered and run from one script:
```powershell
cd "SCH_LPDG_RGMCET_MASTERCLASS\Snowpark\procedures"
python run.py
```
This registers `BUILD_TRAINING_DATA()`, `TRAIN_MODEL()`, and `RUN_INFERENCE()` in Snowflake and
calls them in order. Once registered, they can also be called directly from SQL — including on
new data by passing a table name:
```sql
CALL RUN_INFERENCE('MY_NEW_TABLE', 'MY_PREDICTIONS');
```
