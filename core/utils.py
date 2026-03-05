import json, csv
from config import DATA_DIR, OUTPUT_DIR


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows.extend(reader)
    return rows


def load_input_payload():
    return {
        "source": load_json(DATA_DIR / "source_schema.json"),
        "target": load_json(DATA_DIR / "target_schema.json"),
        "mapping": load_csv(DATA_DIR / "field_mapping.csv")
    }


def save_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def write_outputs(sql_out, validation, explanation):
    OUTPUT_DIR.mkdir(exist_ok=True)

    save_text(
        OUTPUT_DIR / "sample_output.sql",
        "\n\n".join([s["sql"] for s in sql_out["data"]["sql_statements"]])
    )

    save_text(
        OUTPUT_DIR / "validation_report.md",
        validation["data"]["markdown"]
    )

    save_text(
        OUTPUT_DIR / "sql_explanation.md",
        explanation["data"]["explanation"]
    )

def build_validation_markdown(issues):
    """
    Builds markdown report.
    """

    if not issues:
        return (
            "# Validation Report\n\n"
            "## Status\n"
            "SUCCESS\n\n"
            "No migration risks or validation issues were detected.\n"
        )

    badge = {
        "HIGH": " HIGH",
        "MEDIUM": " MEDIUM",
        "LOW": " LOW"
    }

    md = "# Validation Report\n\n"
    md += "## Status\n FAILED\n\n"
    md += "## Issues\n\n"

    for i, issue in enumerate(issues, start=1):

        # SAFE ACCESS (dict OR object)
        if isinstance(issue, dict):
            severity = issue.get("severity", "UNKNOWN")
            message = issue.get("message", "No message")
            suggestion = issue.get("suggestion")
        else:
            severity = getattr(issue, "severity", "UNKNOWN")
            message = getattr(issue, "message", "No message")
            suggestion = getattr(issue, "suggestion", None)

        md += (
            f"### {i}. {badge.get(severity, ' UNKNOWN')}\n"
            f"- **Issue:** {message}\n"
        )

        if suggestion:
            md += f"- **Suggestion:** {suggestion}\n"

        md += "\n"

    return md


def deduplicate_issues(existing, new):
    """
    Deduplicate issues coming from LLM and deterministic checks.
    """
    seen = {
        (i.severity, i.message)
        for i in existing
    }

    merged = list(existing)

    for i in new:
        key = (i["severity"], i["message"])
        if key not in seen:
            merged.append(i)
            seen.add(key)

    return merged