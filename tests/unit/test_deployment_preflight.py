from deploy_samurai.services.deployment.preflight import check_aws_credentials


class FakeCredentials:
    pass


class FakeStsClient:
    def get_caller_identity(self):
        return {
            "Account": "123456789012",
            "Arn": "arn:aws:iam::123456789012:user/tester",
        }


class FakeSession:
    region_name = "us-east-1"

    def __init__(self, credentials=FakeCredentials()) -> None:
        self.credentials = credentials

    def get_credentials(self):
        return self.credentials

    def client(self, service_name: str):
        assert service_name == "sts"
        return FakeStsClient()


def test_check_aws_credentials_passes_when_credentials_and_identity_exist() -> None:
    result = check_aws_credentials(FakeSession())

    assert result.status == "passed"
    assert result.region == "us-east-1"
    assert result.account_id == "123456789012"
    assert result.message == "AWS credentials are valid."


def test_check_aws_credentials_can_skip_identity_verification() -> None:
    result = check_aws_credentials(FakeSession(), verify_identity=False)

    assert result.status == "passed"
    assert result.account_id is None
    assert result.message == "AWS credentials are available."


def test_check_aws_credentials_fails_when_credentials_are_missing() -> None:
    result = check_aws_credentials(FakeSession(credentials=None))

    assert result.status == "failed"
    assert result.message == "AWS credentials were not found."
