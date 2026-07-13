from clinical_inference_workstation.ml.bundle import load_model_bundle
from clinical_inference_workstation.ml.pipeline import run_training_pipeline
from clinical_inference_workstation.ml.synthetic_data import generate_synthetic_case


def test_loaded_model_bundle_should_score_generated_case(tmp_path) -> None:
    output_dir = tmp_path / "bundle"
    run_training_pipeline(output_dir=output_dir, dataset_size=60, image_size=48)

    bundle = load_model_bundle(output_dir)
    probability = bundle.predict_probability(generate_synthetic_case(seed=13, image_size=48).image)

    assert 0.0 <= probability <= 1.0


def test_loaded_compact_cnn_bundle_should_score_generated_case(tmp_path) -> None:
    output_dir = tmp_path / "cnn-bundle"
    run_training_pipeline(
        output_dir=output_dir,
        dataset_size=60,
        image_size=48,
        model_family="compact_cnn",
    )

    bundle = load_model_bundle(output_dir)
    probability = bundle.predict_probability(generate_synthetic_case(seed=17, image_size=48).image)

    assert 0.0 <= probability <= 1.0
