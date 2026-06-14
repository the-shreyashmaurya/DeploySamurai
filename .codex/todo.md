# DeploySamurai Todo

## Phase 0: Foundation
- [x] Create project workspace structure under `.codex`
- [x] Add Python project bootstrap with `uv`
- [x] Define dependency and lockfile workflow
- [x] Set up formatter and linter configuration
- [x] Set up test runner configuration

## Phase 1: Repo Intake
- [x] Validate GitHub repo URL input
- [x] Implement repo cloning with safe temp workspace handling
- [x] Extract root files and folder tree
- [x] Detect language, framework, and package manager
- [x] Write unit tests for repo metadata extraction

## Phase 2: Architecture Reasoning
- [x] Define normalized repo metadata schema
- [x] Implement service boundary heuristics
- [x] Decide modular monolith versus microservices
- [x] Generate architecture summary output
- [ ] Write tests for reasoning outputs and schema validation

## Phase 3: SAM Generation
- [ ] Define SAM artifact model
- [ ] Generate `template.yaml`
- [ ] Generate Lambda handler scaffolds when needed
- [ ] Add resource mapping for API Gateway, DynamoDB, S3, SQS, and EventBridge
- [ ] Write tests for rendered SAM output

## Phase 4: Deployment
- [ ] Add AWS credential preflight checks
- [ ] Implement SAM build and deploy execution
- [ ] Capture stack outputs and deployment logs
- [ ] Add failure handling and retry strategy
- [ ] Write integration tests for deploy helpers where practical

## Phase 5: Verification
- [ ] Implement stack status checks
- [ ] Add endpoint smoke tests
- [ ] Capture verification evidence
- [ ] Return machine-readable pass/fail results
- [ ] Write tests for verification logic

## Phase 6: UX and Polish
- [ ] Add live progress streaming
- [ ] Render job timeline in the UI
- [ ] Improve error messages for common failures
- [ ] Add cost and scaling notes to the analysis report
- [ ] Add final summary export

## Notes
- Pick one checkbox at a time.
- Do not start the next task until the current one is implemented and verified.
- Keep changes small so tests stay trustworthy.
