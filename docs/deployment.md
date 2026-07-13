# Deployment

## Public deployment surface

This repo includes an Azure-ready deployment surface intended as a public reference scaffold:

- `Dockerfile` for the FastAPI service
- `.github/workflows/ci.yml` for test execution
- `.github/workflows/azure-deploy.yml` for OIDC-shaped deployment wiring
- `scripts/verify_deployment.py` for smoke verification

These assets are intentionally generic. They demonstrate deployable service shape without publishing private resource identifiers, credentials, or live environment topology.

What this proves:

- the service can be packaged and verified locally
- the repo has a reasonable CI and deployment seam
- auth and audit behavior are accounted for in the service boundary

What this does not prove:

- a complete live Azure environment
- private infrastructure automation from the original work
- production hosting or operating metrics

## Runtime configuration

Relevant environment variables:

- `STW_AUTH_MODE`
- `STW_JWT_SECRET`
- `STW_JWT_ISSUER`
- `STW_JWT_AUDIENCE`
- `STW_AUDIT_LOG_PATH`

## Local container run

```bash
docker build -t clinical-inference-workstation .
docker run --rm -p 8000:8000 clinical-inference-workstation
```

## Verification

After deployment, verify:

```bash
python scripts/verify_deployment.py --base-url http://127.0.0.1:8000
```

If auth is enabled, pass a bearer token and an inference record ID:

```bash
python scripts/verify_deployment.py --base-url https://example-host --bearer-token "$TOKEN" --inference-id 1
```

## Notes on the workflow

`.github/workflows/azure-deploy.yml` is intentionally conservative. It shows the OIDC login shape and image-build step, but the final deploy command remains a repo-specific placeholder so this public repo does not pretend to expose private infrastructure details.

## Engineering approach

The private work that informed this repository used deployment gates, load testing, and
performance investigation to support service delivery. The relevant public patterns are
represented here: test-gated CI, container packaging, configuration-driven auth and audit
behavior, and a smoke-verification command.

Performance work focused on locating media-processing bottlenecks through asynchronous I/O,
caching, and phase-level instrumentation before applying targeted improvements. This public
reference intentionally omits private topology, targets, and operational measurements.
