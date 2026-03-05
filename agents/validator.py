"""
Verifies data type compatibility and identifies possible errors or missing mappings
Responsibilities of validation agent: Missing Mappings, Unknown columns, Type incompatibility, Dangerous casts,
Nullability Risks, Text length mismatch.
"""

import sqlglot
from sqlglot import exp

from agents.base_agent import BaseAgent
from config import FORBIDDEN_SQL_KEYWORDS
from core.models import ValidationResponse
from core.utils import build_validation_markdown, deduplicate_issues



# helpers
def make_issue(severity, message, suggestion=None):
    return {
        "severity": severity,
        "message": message,
        "suggestion": suggestion
    }


def build_target_schema_index(target_schema):
    """
    {
      table_name -> set(columns)
    }
    """
    index = {}

    for t in target_schema.get("tables", []):
        index[t["table"]] = {
            c["name"] for c in t.get("columns", [])
        }

    return index



# Validation Agent
class ValidationAgent(BaseAgent):

    def run(self, payload):

        self._log_input(payload)

        issues = []

        sql_statements = payload["sql_statements"]
        target_schema = payload["target_schema"]
        schema_warnings = payload.get("schema_warnings", [])

        target_index = build_target_schema_index(target_schema)

        # schema analyst warnings
        for w in schema_warnings:
            issues.append(
                make_issue(
                    severity="HIGH",
                    message=f"Schema analysis warning: {w}",
                    suggestion="Fix mapping or schema before migration."
                )
            )

        #Deterministic SQL + Schema Validation
        for stmt in sql_statements:

            sql = stmt["sql"]

            # forbidden keywords
            for kw in FORBIDDEN_SQL_KEYWORDS:
                if kw in sql.upper():
                    issues.append(
                        make_issue(
                            severity="HIGH",
                            message=f"{stmt['target_table']}: forbidden keyword {kw}",
                            suggestion="Remove forbidden SQL operation."
                        )
                    )

            try:
                parsed = sqlglot.parse_one(sql)

                #Validate inserted columns vs schema
                insert_expr = parsed.find(exp.Insert)

                if insert_expr:

                    table_name = insert_expr.this.this.name

                    if table_name not in target_index:
                        issues.append(
                            make_issue(
                                severity="HIGH",
                                message=f"Target table '{table_name}' not found in target schema.",
                                suggestion="Check mapping target table."
                            )
                        )
                        continue

                    expected_cols = target_index[table_name]

                    columns = [
                        c.name for c in insert_expr.this.expressions
                    ]

                    for col in columns:
                        if col not in expected_cols:
                            issues.append(
                                make_issue(
                                    severity="HIGH",
                                    message=f"{table_name}: column '{col}' not found in target schema.",
                                    suggestion=f"Fix mapping or correct column name (did you mean something else?)."
                                )
                            )

            except Exception as e:
                issues.append(
                    make_issue(
                        severity="HIGH",
                        message=f"{stmt['target_table']}: {str(e)}",
                        suggestion="Fix SQL syntax."
                    )
                )

        # LLM Semantic Validation
        expected_schema = {
            "status": "success",
            "warnings": [],
            "data": {
                "issues": [],
                "markdown": ""
            }
        }

        prompt = f"""
Review these SQL statements for semantic migration risks.

SQL:
{sql_statements}

Return JSON exactly matching:
{expected_schema}
"""

        llm_resp = self.llm.generate_json_typed(
            prompt,
            "validator",
            ValidationResponse
        )

        # merge deterministic + LLM issues
        llm_resp.data.issues = deduplicate_issues(
            llm_resp.data.issues,
            issues
        )

        if llm_resp.data.issues:
            llm_resp.status = "failed"
        else:
            llm_resp.status = "success"

        llm_resp.data.markdown = build_validation_markdown(
            llm_resp.data.issues
        )

        output = llm_resp.model_dump()

        self._log_output(output)
        return output
