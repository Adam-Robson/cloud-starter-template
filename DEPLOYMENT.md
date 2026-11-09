# Deployment

The [Continuous Deployment](.github/workflows/deploy.yml) workflow deploys
the template to Google Cloud Run. It runs after the
[Continuous Integration](.github/workflows/ci.yml) workflow passes on a push
to `main`, and it can also be started by hand from the repository's Actions
tab. The workflow:

1. Authenticates to Google Cloud with Workload Identity Federation. GitHub
   issues a short-lived token that Google exchanges for the deployer service
   account's credentials, so no service account key is ever created.
2. Builds the backend image, pushes it to Artifact Registry, and deploys it
   as the `backend` Cloud Run service with `STORAGE=firestore`.
3. Builds the frontend image, pushes it, and deploys it as the `frontend`
   Cloud Run service with `API_URL` set to the backend's URL, so nginx can
   proxy `/api` requests to it.

Images are tagged with the commit SHA that CI tested, so every Cloud Run
revision can be traced back to an exact commit.

## One-time Google Cloud setup

Nothing in this repository creates cloud resources; the commands below do
it once with the `gcloud` CLI. Run them as a project Owner, after setting
these shell variables:

```sh
PROJECT_ID=<your-project-id>
REGION=us-central1
REPOSITORY=cloud-starter
GITHUB_REPO=<owner>/<repo>
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" \
  --format 'value(projectNumber)')
```

### 1. Enable the APIs

```sh
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  firestore.googleapis.com iam.googleapis.com iamcredentials.googleapis.com \
  sts.googleapis.com --project "$PROJECT_ID"
```

### 2. Create the image repository and the database

The Firestore database must use Native mode and is named `(default)`. Its
location cannot be changed after it is created.

```sh
gcloud artifacts repositories create "$REPOSITORY" \
  --repository-format docker --location "$REGION" --project "$PROJECT_ID"
gcloud firestore databases create --location "$REGION" --project "$PROJECT_ID"
```

### 3. Create the service accounts

Each identity gets only the access it needs:

- `deployer` is used by GitHub Actions. It can push images and deploy Cloud
  Run services, and it can attach the two runtime accounts to them.
- `backend-runtime` is the identity the backend runs as. Its only role is
  `roles/datastore.user`, which allows reading and writing Firestore.
- `frontend-runtime` is the identity nginx runs as. It needs no roles,
  because it only serves files and forwards requests. Without a dedicated
  account, Cloud Run would use the default compute service account, which
  usually has broad Editor access.

```sh
SA_DOMAIN="$PROJECT_ID.iam.gserviceaccount.com"
for account in deployer backend-runtime frontend-runtime; do
  gcloud iam service-accounts create "$account" --project "$PROJECT_ID"
done

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:backend-runtime@$SA_DOMAIN" \
  --role roles/datastore.user
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:deployer@$SA_DOMAIN" --role roles/run.admin
gcloud artifacts repositories add-iam-policy-binding "$REPOSITORY" \
  --location "$REGION" --project "$PROJECT_ID" \
  --member "serviceAccount:deployer@$SA_DOMAIN" \
  --role roles/artifactregistry.writer
for account in backend-runtime frontend-runtime; do
  gcloud iam service-accounts add-iam-policy-binding "$account@$SA_DOMAIN" \
    --project "$PROJECT_ID" \
    --member "serviceAccount:deployer@$SA_DOMAIN" \
    --role roles/iam.serviceAccountUser
done
```

### 4. Trust GitHub Actions with Workload Identity Federation

The provider's attribute condition only accepts tokens issued to this
repository, so workflows in other repositories cannot impersonate the
deployer.

```sh
gcloud iam workload-identity-pools create github \
  --location global --project "$PROJECT_ID"
gcloud iam workload-identity-pools providers create-oidc github \
  --location global --workload-identity-pool github --project "$PROJECT_ID" \
  --issuer-uri https://token.actions.githubusercontent.com \
  --attribute-mapping \
  'google.subject=assertion.sub,attribute.repository=assertion.repository' \
  --attribute-condition "assertion.repository == '$GITHUB_REPO'"

POOL="projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github"
gcloud iam service-accounts add-iam-policy-binding "deployer@$SA_DOMAIN" \
  --project "$PROJECT_ID" --role roles/iam.workloadIdentityUser \
  --member "principalSet://iam.googleapis.com/$POOL/attribute.repository/$GITHUB_REPO"
```

### 5. Set the repository variables

The workflow reads its configuration from GitHub repository variables.
None of these values is a secret, so they are variables rather than
secrets.

```sh
gh variable set GCP_PROJECT_ID --body "$PROJECT_ID"
gh variable set GCP_REGION --body "$REGION"
gh variable set GCP_ARTIFACT_REPOSITORY --body "$REPOSITORY"
gh variable set GCP_WORKLOAD_IDENTITY_PROVIDER --body "$POOL/providers/github"
gh variable set GCP_DEPLOY_SERVICE_ACCOUNT --body "deployer@$SA_DOMAIN"
gh variable set GCP_BACKEND_SERVICE_ACCOUNT --body "backend-runtime@$SA_DOMAIN"
gh variable set GCP_FRONTEND_SERVICE_ACCOUNT --body "frontend-runtime@$SA_DOMAIN"
```

## After the first deployment

Open the `frontend` service's URL, which the Cloud Run console and
`gcloud run services describe frontend --region "$REGION"` both show.

## Things to know

- **The backend is publicly reachable.** Both services are deployed with
  `--allow-unauthenticated`, because nginx forwards requests to the backend
  without attaching a Google identity token. Browsers still only call the
  frontend, but anyone who learns the backend's URL can call it directly.
  Restricting it requires private networking (internal ingress plus VPC
  egress from the frontend), which this template does not set up.
- **Organization policies can block public services.** If your project
  belongs to an organization that enforces Domain Restricted Sharing,
  `--allow-unauthenticated` fails, and an administrator must allow it for
  this project.
- **Images accumulate.** Every deployment pushes two new images. Consider
  adding an Artifact Registry cleanup policy that keeps only recent ones.
- **The deploy workflow must be on `main` to run.** GitHub only starts
  `workflow_run` workflows from the default branch, so automatic deployments
  begin after this workflow is merged.
