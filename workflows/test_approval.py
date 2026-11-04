import logging

from langgraph.types import Command

from workflows.approval_workflow import create_approval_workflow

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

workflow = create_approval_workflow()


def test_approval(incident_id: str, decision: bool):
    config = {"configurable": {"thread_id": incident_id}}

    # Start workflow and pause for human approval
    result = workflow.invoke(
        {
            "incident_id": incident_id,
            "report": (
                "Incident Investigation Report\n"
                "Service: authentication-api\n"
                "Error Rate: 18.5%\n"
                "Possible Cause: Database connection pool exhaustion.\n"
                "Remediation Plan: Evaluate rollback of deployment DEP-1002."
            ),
            "recipient_email": "test@example.com",
            "approved": False,
            "status": "AWAITING_APPROVAL",
            "comments": "",
        },
        config=config,
    )

    assert result.get("__interrupt__"), "Workflow did not pause!"

    print(f"\n[TEST] Incident {incident_id} paused for email approval")

    # Verify the approval request contains the report and recipient
    approval_request = result["__interrupt__"][0].value

    assert approval_request["type"] == "email_approval"
    assert approval_request["recipient_email"] == "test@example.com"
    assert approval_request["report"]

    # Simulate human approval or rejection
    result = workflow.invoke(
        Command(
            resume={
                "approved": decision,
                "comments": "Testing email approval",
            }
        ),
        config=config,
    )

    expected_status = "APPROVED" if decision else "REJECTED"

    assert result["approved"] is decision
    assert result["status"] == expected_status

    print(f"[TEST] Final status: {result['status']}")


# Test both approval and rejection
test_approval("INC-TEST-001", True)
test_approval("INC-TEST-002", False)
