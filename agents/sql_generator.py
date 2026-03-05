"""
Generates SQL SELECT or INSERT statements using LLM.
Responsibilities: Generate deterministic SQL, Use aliases, Apply transforms.
"""

import json

from agents.base_agent import BaseAgent
from core.models import SQLGeneratorResponse


class SQLGeneratorAgent(BaseAgent):

    def run(self, payload, validation_feedback=None):

        self._log_input(payload)

        expected_schema = {
            "status": "success",
            "warnings": [],
            "data": {
                "sql_statements": [
                    {
                        "target_table": "string",
                        "sql": "string"
                    }
                ]
            }
        }

        feedback_section = ""

        if validation_feedback:
            feedback_section = f"""
        IMPORTANT:
        Previous SQL generation failed validation.

        Fix the following validation issues:
        {json.dumps(validation_feedback, indent=2)}

        Regenerate ALL SQL statements with corrections.
        """

        prompt = f"""
You are an expert SQL migration generator.

Generate SQL migration statements from resolved mappings.

{feedback_section}

STRICT RULES:

1. OUTPUT STRUCTURE
- Output MUST be valid JSON.
- JSON must EXACTLY match this structure:

{json.dumps(expected_schema, indent=2)}

- Do NOT add extra fields.
- Do NOT remove required fields.

2. SQL DIALECT
- ANSI SQL compatible.
- Avoid vendor-specific syntax.

3. SQL STATEMENT RULES
- Generate ONE SQL statement per target_table.
- Group mappings by target_table.
- Each statement should INSERT INTO target table.

4. SQL FORMAT
- No markdown.
- No comments.
- Deterministic formatting.
- Use explicit column names.

5. ALIAS RULES
- Always alias source table as: src

Example:
FROM source_table AS src

6. CAST RULES
- Apply cast only if mapping specifies cast.
- If cast is null → use direct column.

7. TRANSFORM RULES
- If transform is provided, apply it.
- Otherwise use source column directly.

8. NULL HANDLING
- Preserve NULL values.
- Do not filter rows.

9. COLUMN ORDER
- Preserve mapping order exactly.


SQL TEMPLATE:
INSERT INTO target_table (
    target_col1,
    target_col2
)
SELECT
    expr1 AS target_col1,
    expr2 AS target_col2
FROM source_table AS src;

RESOLVED MAPPINGS:
{json.dumps(payload["resolved_mappings"], indent=2)}

Return ONLY JSON.
"""

        llm_resp = self.llm.generate_json_typed(
            prompt,
            "sql_generator",
            SQLGeneratorResponse
        )

        output = llm_resp.model_dump()

        self._log_output(output)
        return output
