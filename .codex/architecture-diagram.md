# DeploySamurai Architecture Diagram

## High-Level View

```mermaid
flowchart TD
  U[User] --> F[Flutter Web App]
  F --> API[FastAPI Orchestrator]

  API --> Q[Job State Store]
  API --> EV[SSE / WebSocket Progress Stream]

  API --> RA[Repo Analysis Service]
  RA --> CLONE[GitHub Clone Workspace]
  RA --> META[Repo Metadata]

  API --> AG[Architecture Reasoning Service]
  AG --> PLAN[Service Boundary Plan]
  AG --> DEC[Deployment Decisions]

  API --> SG[SAM Generation Service]
  SG --> SAM[template.yaml + Lambda Stubs]

  API --> DEP[AWS Deployment Service]
  DEP --> AWS[(AWS SAM / CloudFormation)]

  API --> VF[Verification Service]
  VF --> HC[Health Checks]
  VF --> OUT[Deployment Outputs]

  SAM --> ART[S3 Artifact Store]
  DEP --> ART
  VF --> ART
```

## Optional Runtime Layout

```mermaid
flowchart LR
  subgraph Local["Local Dev / Hackathon Machine"]
    FE["Flutter Web Frontend"]
    ORCH["FastAPI Orchestrator"]
    ANALYZE["Repo Analysis"]
    REASON["Architecture Reasoning"]
    GEN["SAM Generation"]
    VERIFY["Verification"]
  end

  subgraph Cloud["AWS"]
    DEPLOY["SAM Deploy Target"]
    LAMBDA["Lambda"]
    APIGW["API Gateway"]
    DDB["DynamoDB"]
    S3["S3"]
    CW["CloudWatch"]
  end

  FE --> ORCH
  ORCH --> ANALYZE
  ORCH --> REASON
  ORCH --> GEN
  ORCH --> VERIFY
  ORCH --> DEPLOY

  DEPLOY --> LAMBDA
  DEPLOY --> APIGW
  DEPLOY --> DDB
  DEPLOY --> S3
  DEPLOY --> CW
```

## Connection Rules

- The frontend should talk only to the orchestrator.
- Services should communicate through explicit JSON contracts.
- The orchestrator owns job state and progress updates.
- The analysis service should not deploy anything.
- The reasoning service should not touch AWS directly.
- The generation service should produce files, not execute deployments.
- The deployment service should be the only component that talks to AWS for create/update actions.
- The verification service should validate what was actually deployed, not what was intended.

## Docker Compose Intent

If we have time later, Docker Compose can be used to run the non-AWS parts locally:
- Flutter web dev server
- FastAPI orchestrator
- analysis service
- reasoning service
- SAM generation service
- verification service
- optional local state store

For v1, Docker Compose is a convenience layer, not a requirement.
It should only be added after the service contracts stabilize.
