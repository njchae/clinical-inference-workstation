from pathlib import Path


def test_readme_should_document_full_public_cli_surface() -> None:
    contents = Path("README.md").read_text(encoding="utf-8")

    assert "Quickstart" in contents
    assert "Verification" in contents
    assert "python scripts/run_adjudication_workflow.py" in contents
    assert "demo-walkthrough.md" in contents
    assert "agentic-adjudication.md" in contents
    assert "python scripts/generate_dataset.py" in contents
    assert "python scripts/calibrate_model.py" in contents
    assert "python scripts/evaluate_model.py" in contents
    assert "python scripts/run_doe_sweep.py" in contents
    assert "python scripts/generate_report.py" in contents
    assert "python scripts/label_images.py" in contents
    assert "python scripts/export_reviewed_labels.py" in contents
    assert "portfolio-context.md" in contents
    assert "capability-map.md" in contents


def test_architecture_doc_should_include_a_system_diagram() -> None:
    contents = Path("docs/architecture.md").read_text(encoding="utf-8")

    assert "```mermaid" in contents


def test_agentic_adjudication_doc_should_describe_roles_and_escalation() -> None:
    contents = Path("docs/agentic-adjudication.md").read_text(encoding="utf-8")

    assert "evidence_collector" in contents
    assert "label_reviewer" in contents
    assert "safety_checker" in contents
    assert "review_router" in contents
    assert "needs_human_review" in contents


def test_demo_walkthrough_should_provide_a_fixed_interview_flow() -> None:
    contents = Path("docs/demo-walkthrough.md").read_text(encoding="utf-8")

    assert "5-7 Minute Demo Walkthrough" in contents
    assert "python scripts/bootstrap_demo.py" in contents
    assert "python scripts/run_api.py" in contents
    assert "artifacts/latest/" in contents
    assert "output/inference_audit.jsonl" in contents


def test_doe_doc_should_describe_the_parameter_sweep() -> None:
    contents = Path("docs/doe-parameter-sweeps.md").read_text(encoding="utf-8")

    assert "full_factorial" in contents
    assert "target_sensitivity" in contents
    assert "validation" in contents
    assert "doe_results.csv" in contents


def test_deployment_doc_should_describe_reference_scaffold_honestly() -> None:
    contents = Path("docs/deployment.md").read_text(encoding="utf-8")

    assert "reference scaffold" in contents
    assert "Azure-ready deployment surface" in contents


def test_public_portfolio_surface_should_not_publish_private_operational_metrics() -> None:
    public_files = [
        Path("README.md"),
        Path("dashboard/app.py"),
        *Path("docs").glob("*.md"),
        *Path("artifacts/latest").glob("*.json"),
        *Path("artifacts/latest").glob("*.md"),
        *Path("artifacts/sore_throat").glob("*.json"),
        *Path("artifacts/sore_throat").glob("*.md"),
    ]
    contents = "\n".join(path.read_text(encoding="utf-8") for path in public_files)

    for private_detail in (
        "n=929",
        "n=722",
        "97.0% sensitivity",
        "6.8% to 95.0%",
        "AUC 0.960",
        "P95 −72%",
        "346 automated tests",
        "199 compliance tests",
        "Container Apps microservices",
        "kappa > 0.75",
    ):
        assert private_detail not in contents


def test_public_reference_cases_should_include_attribution_and_saved_output_scope() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    workstation = Path("web/index.html").read_text(encoding="utf-8")
    app = Path("web/app.js").read_text(encoding="utf-8")
    provenance = Path("docs/reference-image-provenance.md").read_text(encoding="utf-8")
    case_data = Path("web/public-cases.json").read_text(encoding="utf-8")

    assert Path("web/reference-images/otoscopic-reference-01.png").is_file()
    assert Path("web/reference-images/otoscopic-reference-02.png").is_file()
    assert Path("web/reference-images/otoscopic-reference-03.png").is_file()
    assert "eardrum.zip" in readme
    assert "CC BY 4.0" in readme
    assert "Private evaluation metrics and operational measurements are intentionally excluded." in readme
    assert "Recorded inference cases" in workstation
    assert "public-cases.json" in app
    assert "recorded local pipeline output" in workstation
    assert "not a clinical assessment" in workstation
    assert '"pipeline": "local_aom_feature_analysis"' in case_data
    assert '"review_status": "human_review_required"' in case_data
    assert "probability" not in case_data
    assert "threshold" not in case_data
    assert "latency" not in case_data
    assert "10.6084/m9.figshare.13648166.v1" in provenance
