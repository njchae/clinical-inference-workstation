# Task runner for the Clinical Inference Workstation.
# Wraps the CLI scripts so common workflows are one command each.

PYTHON ?= python

.PHONY: help setup dataset train calibrate evaluate sweep report demo api dashboard test verify

help:
	@echo "Targets:"
	@echo "  setup      Install the package (editable) with dev extras"
	@echo "  dataset    Generate synthetic dataset + sample cases"
	@echo "  train      Train the baseline model bundle"
	@echo "  calibrate  Fit temperature scaling and select the review threshold"
	@echo "  evaluate   Evaluate the calibrated model on the held-out test split"
	@echo "  sweep      Run the DOE parameter sweep over temperature x threshold"
	@echo "  report     Render the Markdown algorithm report from artifacts"
	@echo "  demo       One-command bootstrap of the full demo"
	@echo "  api        Serve the inference API"
	@echo "  dashboard  Launch the Streamlit evaluation dashboard"
	@echo "  test       Run the test suite"
	@echo "  verify     Smoke-check a running deployment"

setup:
	$(PYTHON) -m pip install -e ".[dev]"

dataset:
	$(PYTHON) scripts/generate_dataset.py

train:
	$(PYTHON) scripts/train_model.py

calibrate:
	$(PYTHON) scripts/calibrate_model.py

evaluate:
	$(PYTHON) scripts/evaluate_model.py

sweep:
	$(PYTHON) scripts/run_doe_sweep.py --split validation

report:
	$(PYTHON) scripts/generate_report.py

demo:
	$(PYTHON) scripts/bootstrap_demo.py

api:
	$(PYTHON) scripts/run_api.py

dashboard:
	streamlit run dashboard/app.py

test:
	$(PYTHON) -m pytest tests -q

verify:
	$(PYTHON) scripts/verify_deployment.py --base-url http://127.0.0.1:8000
