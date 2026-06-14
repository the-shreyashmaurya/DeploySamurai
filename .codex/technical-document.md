# DeploySamurai Technical Document

## 1. System Overview
DeploySamurai is a Python backend plus Flutter frontend that analyzes a GitHub repository, infers architecture, and optionally deploys an AWS serverless stack with SAM.

Recommended stack:
- Frontend: Flutter
- Backend: FastAPI
- Orchestration: LangGraph
- IaC: AWS SAM
- Runtime and packaging: `uv`
- AWS SDK: `boto3`

## 2. Technical Feasibility
This product is technically feasible if the scope stays narrow.

What is feasible:
- cloning a public or authorized GitHub repository
- reading the repo structure and package metadata
- detecting common stacks
- deriving service candidates from folder and dependency patterns
- generating SAM templates and Lambda stubs
- running `sam build` and `sam deploy`
- checking deployment outputs and basic endpoint health

What is risky:
- fully automatic microservice decomposition for arbitrary codebases
- automatic migration of complex business logic
- broad support for every language/framework
- fully autonomous AWS deployment without guardrails

Conclusion:
- Advisor mode is low-risk and should be built first.
- Autonomous mode is feasible only with approvals, scoped permissions, and good verification.

## 3. Core Architecture
### Frontend
Flutter web app with these screens:
- repo input
- analysis progress
- architecture preview
- deployment console
- final result

### Backend
FastAPI service responsible for:
- GitHub repo ingestion
- job orchestration
- stack detection
- architecture planning
- SAM generation
- deployment execution
- verification
- live progress streaming over SSE or WebSocket

### Internal workflow
1. Intake request.
2. Validate repo URL.
3. Clone repo into an isolated workspace.
4. Extract metadata.
5. Classify stack and app shape.
6. Propose service boundaries.
7. Generate SAM artifacts.
8. Optionally deploy.
9. Verify results.
10. Return structured output.

## 4. uv-Based Project Setup
Use `uv` for:
- creating the virtual environment
- locking dependencies
- running tests
- running scripts
- managing dev dependencies

Recommended workflow:
- `uv init` for project bootstrap
- `uv add` for runtime dependencies
- `uv add --dev` for test and tooling dependencies
- `uv run pytest` for tests
- `uv run ruff check` and `uv run ruff format` for linting and formatting

## 5. Code Quality Standards
- Use type hints everywhere practical.
- Keep business logic in small pure functions where possible.
- Separate orchestration from generation and from AWS calls.
- Validate all API inputs and outputs with Pydantic models.
- Make external calls retryable and observable.
- Avoid hidden global state.
- Keep side effects behind service interfaces.
- Prefer explicit data contracts over ad hoc dictionaries.

## 6. Testing Strategy
Tests should be written and verified for each meaningful change.

Recommended test layers:
- unit tests for parsing, classification, and planning
- contract tests for API request and response models
- generation tests for SAM template output
- integration tests for GitHub clone and repo scanning where practical
- smoke tests for deployment verification helpers

Test priorities:
- schema validation
- repo metadata extraction
- stack detection heuristics
- service boundary output structure
- SAM template rendering
- AWS call wrappers

## 7. Safety and Guardrails
- GitHub URLs must be validated before cloning.
- Repo cloning should use timeouts and size limits.
- Shell execution should be minimized and sanitized.
- AWS credentials should be checked before autonomous mode.
- Deployment should require explicit user approval.
- Generated IAM permissions should be least privilege by default.
- All model outputs should be treated as suggestions, not truth.

## 8. AWS Service Fit
Recommended AWS services:
- Lambda for stateless compute
- API Gateway for synchronous API endpoints
- DynamoDB for job state or analysis snapshots
- S3 for artifacts and generated templates
- SQS for asynchronous jobs
- EventBridge for event fan-out if needed
- CloudWatch for logs and metrics
- IAM for scoped permissions

Use only what each feature needs. Avoid adding services just because they are available.

## 9. Orchestration Design
LangGraph is a good fit because the workflow is:
- stateful
- multi-step
- branchy
- retryable
- easy to model as advisor versus autonomous paths

The orchestration state should include:
- job id
- repo URL
- detected stack
- candidate services
- selected architecture
- generated files
- deployment status
- verification result
- user approval flags

## 10. API Design Notes
- Expose REST endpoints for standard operations.
- Use SSE or WebSocket for live status updates.
- Return structured models instead of free-form text when possible.
- Keep responses stable so the Flutter client can render them reliably.

## 11. Non-Goals for v1
- no multi-cloud deployment
- no Kubernetes output
- no Terraform/CDK support
- no full code migration engine
- no automatic refactoring of the source repo
- no production-grade enterprise discovery across all ecosystems

## 12. Feasibility Verdict
This is a strong hackathon-grade product if built as:
- a repo analyzer
- a reasoning engine
- a SAM generator
- an optional deployer
- a verification layer

The strongest path is to ship Advisor mode first, then add deployment after the plan and contracts are stable.
