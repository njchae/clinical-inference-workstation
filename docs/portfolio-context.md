# Portfolio Context

This repository is a public-safe analogue of private professional work in clinical-image
triage. It preserves the engineering methods and runnable synthetic demonstration while
keeping proprietary implementation, clinical data, and operational evidence private.

## Professional Scope

The work that informed this project covered AOM, impetigo, sore throat, infected insect-bite,
and additional clinical-imaging pathways. Each pathway required its own feature strategy,
evaluation plan, calibration review, and human-escalation policy rather than sharing a single
aggregate model decision.

The public code demonstrates those methods through a synthetic pathway: fixed train,
validation, and held-out evaluation stages; calibration and threshold selection; auditable
inference; and structured machine-assisted label adjudication.

## Engineering Patterns Represented

- Containerized inference-service boundaries with configuration-driven authentication and audit logging.
- Deployment-aware CI and generic OIDC-shaped cloud wiring, without a live environment or private topology.
- Performance investigation through asynchronous I/O, caching, phase-level instrumentation, and load testing.
- Automated quality, privacy, and clinical-safety-minded checks as part of delivery workflows.
- Provider-agnostic, review-aware label adjudication with structured outputs and explicit escalation.

## Intentionally Omitted

- Proprietary source code, schemas, prompts, and clinical data.
- Dataset composition or sizes, model operating points, and production evaluation results.
- Private cloud topology, resource identifiers, deployment targets, and service-level objectives.
- Operational performance measurements, internal test totals, and vendor or tenant details.

## How to Read This Repo

Start with the [README](../README.md) for a repo map, or the [Demo Walkthrough](demo-walkthrough.md) for a guided tour.
