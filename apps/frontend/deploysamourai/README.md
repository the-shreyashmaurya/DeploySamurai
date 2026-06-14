# DeploySamurai Frontend

Flutter web dashboard for DeploySamurai.

## Run Locally

Start the backend from the repository root:

```powershell
uv run uvicorn deploy_samurai.main:app --reload --host 127.0.0.1 --port 8000
```

Start Flutter from this directory:

```powershell
flutter run -d chrome --web-port 8077 --dart-define=API_BASE_URL=http://127.0.0.1:8000/v1
```

`API_BASE_URL` defaults to `http://127.0.0.1:8000/v1`.

## Integrated Endpoints

- `POST /v1/jobs`
- `POST /v1/analyze/repo`
- `POST /v1/reason/architecture`

SAM generation, deployment, and verification remain disabled in the UI until those backend routes are exposed.
