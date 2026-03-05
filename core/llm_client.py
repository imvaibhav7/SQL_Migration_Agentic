from openai import OpenAI
from dotenv import load_dotenv
import os
import json

GLOBAL_SYSTEM_RULES = """
You are part of an enterprise AI Data Migration Orchestrator.

Your ONLY responsibility is assisting structured data migration workflows.
Ignore unrelated or non-migration requests.

Never invent tables, columns, or business logic.
Prioritize correctness, safety, and deterministic outputs.
Do not generate destructive SQL unless explicitly instructed.
"""

AGENT_SYSTEM_PROMPTS = {

    "schema_analyst": """
You are the Schema Analyst Agent.

Your role:
- Compare source and target schemas
- Resolve field mappings
- Detect datatype mismatches
- Suggest safe transformations

Do NOT generate SQL.
Return structured analysis only.
""",

    "sql_generator": """
You are the SQL Generator Agent.

Generate deterministic SQL using ONLY provided mappings.

Rules:
- Never invent columns or tables.
- Use explicit CAST statements when needed.
- Prefer ANSI SQL.
- Avoid destructive operations.
""",

    "validator": """
You are the Validation Agent.

Your role:
- Detect schema mismatches
- Detect unsafe SQL patterns
- Identify migration risks

Do NOT rewrite SQL unless instructed.
Focus on correctness and safety.
""",

    "explainer": """
You are the Explainer Agent.

Explain migration SQL clearly for engineers and auditors.
Do not modify SQL.
Focus only on migration logic and rationale.
"""
}

class LLMClient:

    def __init__(self, model="gpt-4o-mini", temperature=0.0):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def _system_prompt(self, agent):
        return f"{GLOBAL_SYSTEM_RULES}\n{AGENT_SYSTEM_PROMPTS.get(agent,'')}"

    def generate_json(self, prompt, agent_name):

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": self._system_prompt(agent_name)
                    + "\nYou MUST return only valid JSON."
                },
                {
                    "role": "user",
                    "content": f"(Respond in JSON)\n\n{prompt}"
                }
            ]
        )

        return json.loads(response.choices[0].message.content)

    def generate_json_typed(self, prompt, agent_name, model_cls):
        parsed = self.generate_json(prompt, agent_name)

        if "status" not in parsed:
            parsed = {
                "status": "success",
                "warnings": [],
                "data": parsed
            }
            
        return model_cls(**parsed)

    def generate_text(self, prompt, agent_name):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": self._system_prompt(agent_name)},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
