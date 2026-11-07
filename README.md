# cloud-starter-templated

Template scaffold with cloud-native architecture that follows 12-factor app principles, automated
containerization, and the principles of least privilege.

## Google Cloud Platform (GCP)

Organizations → Folders → Projects → Resources

To use any feature of the GCP, the API for the service must be enabled. APIs can be enabled through
creation of a project, which serves as the boundary for a contained billable resource.

Access Management is reached two ways, through a user account (human), or through a service
account (application).

Cloud Run is the target compute platform for this template; it is a managed, serverless Knative
platform that runs containers, scales to zero (will not consume resources when idle), includes
built-in HTTPS endpoints, and supports automated revision management.

## Architecture

```txt
cloud-starter-template/
├── .github/
│   └── workflows/
│       └── deploy.yaml
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── config.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .dockerignore
├── terraform/
│   ├── main.tf
│   └── variables.tf
├── .gitignore
└── README.md
```

## Local Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (installs Python >= 3.13 for you)
- Node.js 22 or 24, with npm

### Install

```sh
cd backend && uv sync
cd ../frontend && npm install
```

### Run

Start the backend and frontend in two terminals:

```sh
# Terminal 1: API on http://localhost:8080
cd backend
uv run backend
```

```sh
# Terminal 2: SPA on http://localhost:5173
cd frontend
npm run dev
```

Open <http://localhost:5173>. The browser only talks to `/api` on its own
origin; the Vite dev server proxies it to the backend on port 8080, as nginx
does in production. Check the API directly with
`curl http://localhost:8080/api/health`, or browse its docs at
<http://localhost:8080/docs>.

### Configuration

The backend reads its settings from the environment, or from a `.env` file in
`backend/`. The defaults work locally with no setup: items are kept in memory
and are lost when the server stops. To use Firestore instead:

```sh
gcloud auth application-default login
cd backend
STORAGE=firestore GCP_PROJECT_ID=<sandbox-project> uv run backend
```

See [backend/README.md](backend/README.md) for every variable. If the backend
runs on a port other than 8080, update the proxy in `frontend/vite.config.ts`.

### API Contract

The frontend's types are generated from the backend's OpenAPI schema. After
changing a backend model or route, regenerate them:

```sh
cd frontend
npm run gen:api
```

### Checks

All must pass before committing:

```sh
# backend/
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest

# frontend/
npm run typecheck
npm run lint
npm test
```

## Backend

The backend for this template scaffolds in Python using FastAPI.

## Frontend

## Infrastructure As Code
