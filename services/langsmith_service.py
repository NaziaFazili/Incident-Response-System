from langsmith import traceable


@traceable(name="Agent Report", run_type="chain")
def record_agent_report(incident_id: str, agent: str, report: str):
    return {"incident_id": incident_id, "agent": agent, "report": report}
