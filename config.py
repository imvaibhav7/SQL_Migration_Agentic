from pathlib import Path

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

MODEL_NAME = "gpt-4o-mini"

FORBIDDEN_SQL_KEYWORDS = ["DELETE", "DROP", "UPDATE", "ALTER"]