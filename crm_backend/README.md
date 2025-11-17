# CRM Backend (FastAPI)

This container provides the FastAPI backend scaffold for the Secure CRM platform. It avoids any file path coupling to the database container and uses environment variables exclusively for DB configuration. There are no references to any db_visualizer tools or folders; database connectivity is configured solely via environment variables as shown below.

## Build

```bash
# from secure-crm-platform-40906-40915/crm_backend
docker build -t crm_backend:local .
```

## Run

```bash
# Optionally create a .env file from the example
cp .env.example .env

# Run with environment file
docker run --rm -p 3001:3001 --env-file .env crm_backend:local
```

## Health Check

- Liveness/Readiness: `GET http://localhost:3001/health`
- Root status: `GET http://localhost:3001/`
- WebSocket help: `GET http://localhost:3001/ws/help`

The health endpoints report whether database configuration environment variables are present, but do not attempt a DB connection in this minimal scaffold.

## Environment Variables

The backend reads these variables if present (no hard-coded paths to the database container):

- CRM_DB_HOST / DB_HOST
- CRM_DB_PORT / DB_PORT
- CRM_DB_NAME / DB_NAME
- CRM_DB_USER / DB_USER
- CRM_DB_PASSWORD / DB_PASSWORD

These are used only for configuration signaling at this stage.
