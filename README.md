# cloud-starter-template

Cloud-native full-stack template architecture that follows 12-factor app
principles, automated containerization and the principles of least
privilege.

## Google Cloud Platform (GCP)

Organizations → Folders → Projects → Resources

To use any feature of GCP, the API for that service must be enabled in a
project. The project is the boundary for billing, enabled APIs and access
control.

Access is granted to two kinds of identity: user accounts, which belong to
people, and service accounts, which belong to applications. This template
never uses service account key files. Locally, the Google client libraries
use your own login through Application Default Credentials; on Cloud Run,
they use the service account attached to the service.

Cloud Run is the target compute platform for this template. It is a
managed, serverless platform that runs containers, scales to zero (it uses
no resources when idle), provides HTTPS endpoints, and keeps a history of
revisions.

## Architecture

The browser only talks to `/api` on its own origin. In development, the
Vite dev server proxies `/api` to the backend; in production, nginx in the
frontend container does the same. The backend stores items in memory by
default, or in Firestore when `STORAGE=firestore`.

```txt
cloud-starter-template/
├── .github/workflows/
│   ├── ci.yml                  # lint, typecheck, test and build
│   └── deploy.yml              # build images and deploy to Cloud Run
├── backend/                    # Python API (FastAPI), managed by uv
│   ├── src/backend/
│   │   ├── main.py             # loads .env, builds Settings, serves app
│   │   ├── app.py              # create_app(settings, ...)
│   │   ├── config/             # Settings, read from the environment
│   │   ├── routes/             # /api/health and /api/items
│   │   ├── db/                 # ItemRepository: in-memory or Firestore
│   │   ├── clients/            # AsyncHttpClient for outbound HTTP
│   │   ├── lib/                # shared models and exceptions
│   │   └── services/           # export-openapi command
│   ├── test/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/                   # React + TypeScript SPA (Vite)
│   ├── src/
│   │   ├── api/                # generated schema and typed API client
│   │   ├── context/            # ApiProvider and useApiClient()
│   │   ├── hooks/              # one TanStack Query hook per operation
│   │   ├── lib/                # components and types
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── test/
│   ├── nginx/default.conf.template
│   ├── Dockerfile
│   ├── openapi.json            # generated from the backend
│   ├── package.json
│   └── vite.config.ts
├── DEPLOYMENT.md
└── README.md
```

## Local Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (installs Python >= 3.13)
- Node.js 22 or 24, with npm
- The [gcloud CLI](https://cloud.google.com/sdk/docs/install), only if you
  use Firestore or deploy

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

Open <http://localhost:5173>. Check the API directly with
`curl http://localhost:8080/api/health`, or browse its docs at
<http://localhost:8080/docs>.

### Configuration

The backend reads its settings from the environment, or from a `.env` file
in `backend/`. Variables already set in the shell take priority over
`.env`. The defaults work locally with no setup: items are kept in memory
and are lost when the server stops. To use Firestore instead, you need a
project with the Firestore API enabled and a Native mode `(default)`
database (see [DEPLOYMENT.md](DEPLOYMENT.md)), and an account allowed to
use it:

```sh
gcloud auth application-default login
gcloud auth application-default set-quota-project <sandbox-project>
cd backend
STORAGE=firestore GCP_PROJECT_ID=<sandbox-project> uv run backend
```

Every local run then reads and writes real data in that project, so use a
sandbox project. See [backend/README.md](backend/README.md) for every
variable. If the backend runs on a port other than 8080, update the proxy
in `frontend/vite.config.ts`.

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

A FastAPI application built by `create_app(settings)`, so tests can inject
their own dependencies. Routes depend on the `ItemRepository` protocol, and
`create_item_repository(settings)` picks the in-memory or Firestore store.
Every error is returned in one `ErrorResponse` shape. The container runs
uvicorn as an unprivileged user on `$PORT`. See
[backend/README.md](backend/README.md).

## Frontend

A React single-page application. It calls the API through a typed
`openapi-fetch` client, provided by `ApiProvider`, and TanStack Query hooks
in `src/hooks/`. The production image is built in two stages: Node compiles
the static bundle, and an unprivileged nginx serves it, proxying `/api/` to
the URL in `API_URL`.

## Continuous Integration and Deployment

[ci.yml](.github/workflows/ci.yml) runs the backend checks on Python 3.13
and 3.14, and the frontend checks and build on Node 22 and 24, for pushes
and pull requests to `main`.

[deploy.yml](.github/workflows/deploy.yml) runs after CI passes on `main`.
It builds both images, pushes them to Artifact Registry, and deploys them
to Cloud Run, authenticating with Workload Identity Federation. Cloud
resources are created once with `gcloud`, as described in
[DEPLOYMENT.md](DEPLOYMENT.md); this template does not use Terraform.
