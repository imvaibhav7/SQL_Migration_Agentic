from agents.schema_analyst import SchemaAnalystAgent
from agents.sql_generator import SQLGeneratorAgent
from agents.validator import ValidationAgent
from agents.explainer import ExplainerAgent

from agents.orchestrator import build_orchestration_graph

from core.utils import load_input_payload, write_outputs
from core.llm_client import LLMClient


def main():

    print("Starting AI Data Migration Orchestrator...")

    llm = LLMClient()

    # Initialize agents
    agents = {
        "schema_analyst": SchemaAnalystAgent(llm),
        "sql_generator": SQLGeneratorAgent(llm),
        "validator": ValidationAgent(llm),
        "explainer": ExplainerAgent(llm),
    }

    # Build workflow
    app = build_orchestration_graph(agents)

    input_payload = load_input_payload()

    initial_state = {
        "input_payload": input_payload,
        "analysis": None,
        "sql_output": None,
        "validation": None,
        "explanation": None,
        "validation_feedback": None,
        "retry_count": 0,
    }

    # Execute workflow
    final_state = app.invoke(initial_state)

    # Safety checks
    if not final_state.get("sql_output"):
        raise RuntimeError("SQL generation failed.")

    if not final_state.get("validation"):
        raise RuntimeError("Validation step failed.")

    if not final_state.get("explanation"):
        raise RuntimeError("Explainer step failed.")

    # Write outputs
    write_outputs(
        sql_out=final_state["sql_output"],
        validation=final_state["validation"],
        explanation=final_state["explanation"],
    )

    print(" Migration artifacts generated.")


if __name__ == "__main__":
    main()
