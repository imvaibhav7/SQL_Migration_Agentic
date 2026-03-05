import json
from config import LOG_DIR


def log_agent_io(agent_name, stage, payload):
    LOG_DIR.mkdir(exist_ok=True)

    path = LOG_DIR / f"{agent_name}_{stage}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

