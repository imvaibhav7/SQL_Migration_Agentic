"""
Reads the source and target schemas, extracts structure, detects mismatches.
Responsibilities: compare schemas, detect missing columns, infer casts, generate enriched mapping.
"""

import json
from agents.base_agent import BaseAgent
from core.models import SchemaAnalystResponse


def build_schema_index(schema):
    """
    Build lookup:
    {(table, column): type}
    """
    index = {}

    for t in schema.get("tables", []):
        for c in t.get("columns", []):
            index[(t["table"], c["name"])] = c["type"]

    return index


class SchemaAnalystAgent(BaseAgent):

    def run(self, payload):

        self._log_input(payload)

        source_schema = payload["source"]
        target_schema = payload["target"]
        mapping = payload["mapping"]

        source_index = build_schema_index(source_schema)
        target_index = build_schema_index(target_schema)

        warnings = []
        base_rows = []

        
        #deterministic grounding
        for m in mapping:

            s_key = (m["source_table"], m["source_field"])
            t_key = (m["target_table"], m["target_field"])

            source_exists = s_key in source_index
            target_exists = t_key in target_index

            source_type = source_index.get(s_key)
            target_type = target_index.get(t_key)

            cast = None
            if source_exists and target_exists:
                if source_type != target_type:
                    cast = target_type

            if not source_exists:
                warnings.append(f"Missing source column: {s_key}")

            if not target_exists:
                warnings.append(f"Missing target column: {t_key}")

            # IMPORTANT:
            # never drop rows — preserve everything
            base_rows.append({
                "source_table": m["source_table"],
                "source": m["source_field"],
                "target_table": m["target_table"],
                "target": m["target_field"],
                "source_type": source_type,
                "target_type": target_type,
                "source_exists": source_exists,
                "target_exists": target_exists,
                "cast": cast,
                "transform": m.get("transform") or None
            })

        # LLM LAYER — reasoning
        prompt = f"""
You are a schema analyst assistant.

You receive validated mappings created by deterministic logic.

Your job:
- improve cast suggestions if needed
- suggest safe transformations
- add warnings for risky mappings
- DO NOT remove mappings
- DO NOT invent new mappings

Validated mappings:
{json.dumps(base_rows, indent=2)}

Return JSON EXACTLY:

{{
  "status": "success",
  "warnings": [],
  "data": {{
    "resolved_mappings": [
      {{
        "source_table": "...",
        "source": "...",
        "target_table": "...",
        "target": "...",
        "cast": null,
        "transform": null
      }}
    ]
  }}
}}

Rules:
- Preserve number of mappings exactly.
- Keep table/column names unchanged.
- If unsure, keep existing values.
"""

        try:
            llm_response = self.llm.generate_json_typed(
                prompt,
                "schema_analyst",
                SchemaAnalystResponse
            )

            resolved = llm_response.data.resolved_mappings

            # safety: ensure row count unchanged
            if len(resolved) != len(base_rows):
                warnings.append(
                    "LLM changed mapping count; falling back to deterministic output."
                )
                raise ValueError("row count mismatch")

            output_obj = llm_response

            # merge warnings
            output_obj.warnings.extend(warnings)

        except Exception:
            #FALLBACK
            output_obj = SchemaAnalystResponse(
                status="partial_success",
                warnings=warnings,
                data={
                    "resolved_mappings": [
                        {
                            "source_table": r["source_table"],
                            "source": r["source"],
                            "target_table": r["target_table"],
                            "target": r["target"],
                            "cast": r["cast"],
                            "transform": r["transform"]
                        }
                        for r in base_rows
                    ]
                }
            )

        output = output_obj.model_dump()

        self._log_output(output)
        return output
