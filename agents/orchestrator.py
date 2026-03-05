from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END


# Shared workflow state
class WorkflowState(TypedDict):
    input_payload: dict
    analysis: Optional[dict]
    sql_output: Optional[dict]
    validation: Optional[dict]
    explanation: Optional[dict]
    validation_feedback: Optional[List[dict]]
    retry_count: int


# Node functions
def schema_analysis_node(state, agents):
    result = agents["schema_analyst"].run(
        state["input_payload"]
    )
    return {"analysis": result}


def sql_generation_node(state, agents):
    result = agents["sql_generator"].run(
        state["analysis"]["data"],
        validation_feedback=state.get("validation_feedback")
    )
    return {"sql_output": result}


def validation_node(state, agents):
    """
    Validator now receives:
    - generated SQL
    - target schema
    - warnings from schema analyst
    """

    result = agents["validator"].run({
        "sql_statements": state["sql_output"]["data"]["sql_statements"],
        "target_schema": state["input_payload"]["target"],
        "schema_warnings": state["analysis"].get("warnings", [])
    })

    updates = {"validation": result}

    if result["status"] != "success":
        updates["validation_feedback"] = result["data"]["issues"]
        updates["retry_count"] = state["retry_count"] + 1

    return updates



def explainer_node(state, agents):
    result = agents["explainer"].run(
        state["sql_output"]["data"]
    )
    return {"explanation": result}


# Routing logic
MAX_RETRIES = 3


def validation_router(state):
    validation = state["validation"]

    if validation["status"] == "success":
        return "explainer"

    if state["retry_count"] >= MAX_RETRIES:
        return "explainer"   # best effort output

    return "sql_generator"


# Build graph
def build_orchestration_graph(agents):

    graph = StateGraph(WorkflowState)

    graph.add_node("schema_analyst",
                   lambda s: schema_analysis_node(s, agents))

    graph.add_node("sql_generator",
                   lambda s: sql_generation_node(s, agents))

    graph.add_node("validator",
                   lambda s: validation_node(s, agents))

    graph.add_node("explainer",
                   lambda s: explainer_node(s, agents))

    graph.set_entry_point("schema_analyst")

    graph.add_edge("schema_analyst", "sql_generator")
    graph.add_edge("sql_generator", "validator")

    graph.add_conditional_edges(
        "validator",
        validation_router,
        {
            "sql_generator": "sql_generator",
            "explainer": "explainer"
        }
    )

    graph.add_edge("explainer", END)

    return graph.compile()
