# DeploySamurai Detailed Project Plan

## 1. Product Summary
DeploySamurai is an AI-assisted AWS serverless architect for GitHub repositories.
It supports two modes:
- Advisor mode: analyze a repo and recommend a serverless microservice architecture.
- Autonomous mode: generate SAM infrastructure and deploy it to AWS.

## 2. Product Goals
- Turn a GitHub repo into a clear serverless architecture recommendation.
- Produce a deployable AWS SAM scaffold.
- Optionally deploy and verify the stack in AWS.
- Show live progress so the user can trust the workflow.

## 3. Scope Lock
Supported input:
- GitHub repository URL only.

Not supported in v1:
- local zip upload
- file upload
- prompt-only app description
- multi-cloud
- Kubernetes
- Terraform
- CDK
- general infrastructure-as-code frameworks beyond SAM

## 4. MVP Constraints
- One repo at a time.
- One deployment target: AWS serverless via SAM.
- Support 1 to 2 common stacks first, ideally Python and Node.js/TypeScript.
- Keep service decomposition to 3 to 5 services maximum.
- Prefer a believable architecture over over-engineering.

## 5. User Journeys
### Advisor mode
1. User pastes GitHub repo URL.
2. System clones the repo and inspects the stack.
3. System identifies likely domains and service boundaries.
4. System recommends AWS services and communication patterns.
5. System shows a SAM scaffold plan and next steps.

### Autonomous mode
1. User pastes GitHub repo URL.
2. System generates a plan and requests approval.
3. System writes SAM files and related scaffolding.
4. System deploys the stack to AWS.
5. System verifies the result and returns outputs.

## 6. Phased Delivery Plan
### Phase 0: Product and repo setup
- Define the workspace layout.
- Add docs, contracts, and task tracking.
- Establish uv-based Python workflow.

### Phase 1: Repo intake and stack detection
- Clone GitHub repositories safely.
- Detect language, framework, build tool, and test tool.
- Parse folder structure and entry points.
- Emit structured repo metadata.

### Phase 2: Architecture reasoning
- Identify bounded contexts and service candidates.
- Decide modular monolith versus split services.
- Map synchronous and asynchronous flows.
- Generate an architecture recommendation.

### Phase 3: SAM generation
- Produce template.yaml.
- Generate Lambda handler stubs where needed.
- Include API Gateway, DynamoDB, S3, SQS, EventBridge, IAM, and CloudWatch only when justified.

### Phase 4: Deployment and verification
- Run SAM deploy in autonomous mode.
- Capture stack outputs.
- Run smoke tests and health checks.
- Summarize success or failure.

### Phase 5: Product polish
- Add streaming progress.
- Improve error handling.
- Add retry and timeout controls.
- Add cost and scaling notes.

## 7. Implementation Principles
- Start with the simplest architecture that can work.
- Make every step observable and testable.
- Keep domain logic separate from orchestration.
- Treat LLM output as untrusted input that must be validated.
- Never let deployment logic depend on free-form text without schema checks.

## 8. Recommended Build Order
1. Repo intake and metadata extraction.
2. Stack detection and file parsing.
3. Service boundary reasoning.
4. SAM template generation.
5. Deployment orchestration.
6. Verification and reporting.
7. UI streaming and progress polish.

## 9. Success Criteria
- A valid GitHub URL can be analyzed end to end.
- The system outputs a useful architecture plan.
- SAM scaffolding is generated successfully.
- Deployment can be attempted in autonomous mode.
- Verification reports a clear result.

## 10. Risks
- GitHub repos vary widely in structure and quality.
- Monorepos and unusual build systems can confuse stack detection.
- AWS credentials and permissions can fail at deploy time.
- Generated IAM permissions can be too broad if not constrained.
- LLM-driven planning can hallucinate dependencies or service boundaries.

## 11. Risk Mitigations
- Validate input with strict schemas.
- Use deterministic parsing before LLM reasoning.
- Keep AWS permissions minimal and explicit.
- Add dry-run and advisor-only mode.
- Write tests for parsing, planning, and generation helpers.

## 12. Definition of Done for MVP
- Advisor mode works reliably on a sample repo.
- Autonomous mode can generate a SAM scaffold.
- Deployment path is documented and gated.
- Verification returns a machine-readable result.
- The team can extend the system from the saved docs.
