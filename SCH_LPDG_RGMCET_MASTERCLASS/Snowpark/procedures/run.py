import sys
from pathlib import Path

PROCEDURES_DIR = Path(__file__).resolve().parent
SNOWPARK_DIR = PROCEDURES_DIR.parent

if str(SNOWPARK_DIR) not in sys.path:
    sys.path.append(str(SNOWPARK_DIR))

from src.utils.snowflake_connection import get_session

session = get_session("dev")

# Register all procedures
SQL_FILES = [
    PROCEDURES_DIR / "Data_Preprocessing.sql",
    PROCEDURES_DIR / "Model_training.sql",
    PROCEDURES_DIR / "Model_Inference.sql",
]

for sql_file in SQL_FILES:
    session.sql(sql_file.read_text()).collect()
    print(f"Registered: {sql_file.name}")

# Run the pipeline: build features -> train + register -> predict
print(session.sql("CALL BUILD_TRAINING_DATA()").collect())
print(session.sql("CALL TRAIN_MODEL()").collect())
print(session.sql("CALL RUN_INFERENCE()").collect())

session.close()
