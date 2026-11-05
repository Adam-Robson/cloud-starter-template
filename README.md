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

## Backend

The backend for this template scaffolds in Python using FastAPI.

## Frontend

## Infrastructure As Code



 
