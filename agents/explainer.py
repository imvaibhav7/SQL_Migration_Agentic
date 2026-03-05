"""
Explainer Agent	Writes a human-readable explanation of the generated SQL for auditability
Responsibilities: Produces audit explaination: what each field does, why cast exist, migration intent.
"""

import json
from agents.base_agent import BaseAgent
from core.models import ExplainerResponse


class ExplainerAgent(BaseAgent):

    def run(self, payload):

        self._log_input(payload)

        prompt = f"""
Explain the following migration SQL for auditors.

SQL:{payload['sql_statements']}
"""

        text = self.llm.generate_text(
            prompt,
            "explainer"
        )

        output = ExplainerResponse(
            status="success",
            warnings=[],
            data={"explanation": text}
        ).model_dump()

        self._log_output(output)
        return output
