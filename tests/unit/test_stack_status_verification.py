from deploy_samurai.services.verification.stack_status import check_stack_status


class FakeCloudFormationClient:
    def __init__(self, response=None, error: Exception | None = None) -> None:
        self.response = response or {}
        self.error = error

    def describe_stacks(self, StackName: str):
        if self.error is not None:
            raise self.error
        return self.response


def test_check_stack_status_passes_for_complete_stack() -> None:
    check = check_stack_status(
        "deploy-samurai-dev",
        FakeCloudFormationClient(
            {
                "Stacks": [
                    {
                        "StackName": "deploy-samurai-dev",
                        "StackStatus": "CREATE_COMPLETE",
                    }
                ]
            }
        ),
    )

    assert check.status == "passed"
    assert check.evidence == "Stack deploy-samurai-dev status is CREATE_COMPLETE."


def test_check_stack_status_fails_for_failed_stack() -> None:
    check = check_stack_status(
        "deploy-samurai-dev",
        FakeCloudFormationClient({"Stacks": [{"StackStatus": "ROLLBACK_COMPLETE"}]}),
    )

    assert check.status == "failed"
    assert "ROLLBACK_COMPLETE" in check.evidence


def test_check_stack_status_fails_when_stack_lookup_errors() -> None:
    check = check_stack_status(
        "missing-stack",
        FakeCloudFormationClient(error=RuntimeError("not found")),
    )

    assert check.status == "failed"
    assert "Unable to describe stack missing-stack" in check.evidence
