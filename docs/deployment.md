# Deployment status and instructions

**Current status: not deployed.** The application is verified locally; no live URL is claimed.

## Local run

Follow the installation steps in the repository README. Run the API with Uvicorn and the React development server in separate terminals. For a production-like local check, run the frontend production build and use the project's documented API workflow.

## Hosting assessment (checked 2026-10-28)

Vercel Hobby currently lists free monthly function usage, but Vercel Functions have a read-only filesystem with writable `/tmp` scratch space; that is not durable database storage. Render's free web services have an ephemeral filesystem and spin down when idle; its free Postgres database expires after 30 days. Therefore the current SQLite-based app should not be publicly deployed as a persistent evaluation tool on those free services.

References: [Vercel Hobby plan](https://vercel.com/docs/plans/hobby), [Vercel function runtime filesystem](https://vercel.com/docs/functions/runtimes), [Render free services and databases](https://render.com/docs/free).

## Required before a public interactive deployment
Annotations and audit events are stored in SQLite, while reviewer IDs are not authenticated identities. Before public hosting, add authentication/authorization, persistent database storage, privacy/retention controls, and an API URL configuration. Verify independent reviews, adjudication, audit history, metrics, and exports after deployment.

After those prerequisites, deploy the backend to a host with durable database storage, configure the production API URL and CORS, deploy the static frontend, set secrets through the host dashboard, and run live health, main-workflow, error-path, and persistence-across-restart smoke checks. Never put `.env` files or credentials into the repository.

Until then, use the documented local setup with synthetic data. Do not submit confidential or personal data to the demo.

