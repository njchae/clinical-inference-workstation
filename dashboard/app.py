"""Evaluation dashboard — reads pre-generated artifacts, no model training required."""

import json
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from clinical_inference_workstation.doe.grid import build_metric_grid, read_doe_results

ARTIFACTS_ROOT = Path(__file__).parent.parent / "artifacts"

PATHWAYS = {
    "Synthetic Triage (runnable demo)": "latest",
}


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def roc_from_predictions(probs: list[float], labels: list[int]):
    """Compute ROC curve without sklearn."""
    thresholds = sorted(set(probs + [0.0, 1.0]), reverse=True)
    tpr_list, fpr_list = [], []
    pos = sum(labels)
    neg = len(labels) - pos
    for t in thresholds:
        tp = sum(1 for p, l in zip(probs, labels) if p >= t and l == 1)
        fp = sum(1 for p, l in zip(probs, labels) if p >= t and l == 0)
        tpr_list.append(tp / pos if pos else 0)
        fpr_list.append(fp / neg if neg else 0)
    return fpr_list, tpr_list


def auc_trapz(fpr: list[float], tpr: list[float]) -> float:
    return abs(sum(
        (fpr[i] - fpr[i - 1]) * (tpr[i] + tpr[i - 1]) / 2
        for i in range(1, len(fpr))
    ))


def render_doe_heatmap(artifact_dir: Path):
    csv_path = artifact_dir / "doe_results.csv"
    if not csv_path.exists():
        return

    st.subheader("DOE Parameter Sweep")
    st.caption(
        "Grid sweep over calibration temperature x review threshold on the validation "
        "split. Each cell is scored with the pipeline's own calibration and metric "
        "functions; the marked cell is the best specificity among cells meeting the "
        "sensitivity target."
    )

    rows = read_doe_results(csv_path)
    if not rows:
        return

    metric = st.selectbox("Metric", ["specificity", "sensitivity", "accuracy"], index=0)
    grid = build_metric_grid(rows, metric=metric)

    fig = go.Figure(
        data=go.Heatmap(
            x=grid.temperatures,
            y=grid.thresholds,
            z=grid.z,
            colorscale="Viridis",
            colorbar=dict(title=metric.capitalize()),
            hovertemplate="temperature=%{x}<br>threshold=%{y}<br>" + metric + "=%{z}<extra></extra>",
        )
    )
    if grid.best is not None:
        fig.add_trace(
            go.Scatter(
                x=[grid.best.temperature],
                y=[grid.best.threshold],
                mode="markers",
                marker=dict(symbol="star", size=16, color="white", line=dict(color="black", width=1)),
                name="Best cell",
                hovertemplate=(
                    f"best<br>temperature={grid.best.temperature}<br>"
                    f"threshold={grid.best.threshold}<br>{metric}={grid.best.value}<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        xaxis_title="Calibration temperature",
        yaxis_title="Review threshold",
        height=420,
        margin=dict(l=40, r=20, t=20, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    if grid.best is not None:
        st.success(
            f"**Best cell:** temperature {grid.best.temperature}, threshold "
            f"{grid.best.threshold} — {metric} {grid.best.value:.4f}"
        )
    else:
        st.warning("No swept cell met the sensitivity target.")


def render_synthetic_pathway(artifact_dir: Path):
    metrics = load_json(artifact_dir / "metrics.json")
    calibration = load_json(artifact_dir / "calibration.json")
    thresholds = load_json(artifact_dir / "thresholds.json")
    predictions = load_json(artifact_dir / "predictions.json")
    comparison = load_json(artifact_dir / "comparison.json")

    st.subheader("Model Performance")
    if metrics:
        c1, c2, c3 = st.columns(3)
        c1.metric("Sensitivity", f"{metrics['sensitivity']:.1%}")
        c2.metric("Specificity", f"{metrics['specificity']:.1%}")
        c3.metric("Accuracy", f"{metrics['accuracy']:.1%}")
        st.caption(
            "Scores on fully synthetic held-out test set. "
            "Interpret as pipeline validation, not clinical performance."
        )

    if predictions:
        st.subheader("ROC Curve — Test Set")
        probs = predictions["test"]["probabilities"]
        labels = predictions["test"]["labels"]
        fpr, tpr = roc_from_predictions(probs, labels)
        auc = auc_trapz(fpr, tpr)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"AUC = {auc:.3f}"))
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines",
                                  line=dict(dash="dash", color="gray"), name="Chance"))
        fig.update_layout(
            xaxis_title="False Positive Rate (1 − Specificity)",
            yaxis_title="True Positive Rate (Sensitivity)",
            height=380, margin=dict(l=40, r=20, t=20, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    if calibration:
        st.subheader("Calibration")
        col1, col2 = st.columns(2)
        col1.metric("Temperature", calibration.get("temperature", "—"))
        col1.metric("Review Threshold", calibration.get("review_threshold", "—"))
        if "finding" in calibration:
            col2.info(calibration["finding"])
        if "result" in calibration:
            st.success(f"**Result:** {calibration['result']}")
        if "lesson" in calibration:
            st.caption(f"*Lesson:* {calibration['lesson']}")

    if comparison:
        st.subheader("Model Family Comparison")
        st.caption(comparison.get("note", ""))
        families = comparison.get("model_families", {})
        rows = []
        for name, data in families.items():
            rows.append({
                "Model": name,
                "Sensitivity": f"{data['sensitivity']:.1%}",
                "Specificity": f"{data['specificity']:.1%}",
                "Accuracy": f"{data['accuracy']:.1%}",
                "Temperature": data["calibration_temperature"],
            })
        st.table(rows)
        if "tradeoffs" in comparison:
            st.info(comparison["tradeoffs"])

    render_doe_heatmap(artifact_dir)


def main():
    st.set_page_config(
        page_title="Synthetic Triage Workstation — Evaluation Dashboard",
        page_icon="🩺",
        layout="wide",
    )
    st.title("Evaluation Dashboard")
    st.markdown(
        "Reads pre-generated evaluation artifacts. No model training required. "
        "See [`docs/portfolio-context.md`](../docs/portfolio-context.md) for project scope."
    )

    pathway_label = st.sidebar.selectbox("Pathway", list(PATHWAYS.keys()))
    artifact_subdir = PATHWAYS[pathway_label]
    artifact_dir = ARTIFACTS_ROOT / artifact_subdir

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Artifact directory**")
    st.sidebar.code(f"artifacts/{artifact_subdir}/")

    model_card_path = artifact_dir / "MODEL_CARD.md"
    if model_card_path.exists():
        with st.sidebar.expander("Model Card"):
            st.markdown(model_card_path.read_text())

    if artifact_subdir == "latest":
        render_synthetic_pathway(artifact_dir)
    else:
        st.warning(f"No renderer registered for pathway: {artifact_subdir}")


if __name__ == "__main__":
    main()
