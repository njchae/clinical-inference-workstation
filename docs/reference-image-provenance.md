# Reference Image Provenance

## Otoscopic saved-case images

`web/reference-images/otoscopic-reference-01.png`,
`web/reference-images/otoscopic-reference-02.png`, and
`web/reference-images/otoscopic-reference-03.png` are adapted from the **eardrum.zip** dataset:

- Kemal Polat (2021), *eardrum.zip*, Figshare.
- DOI: [10.6084/m9.figshare.13648166.v1](https://doi.org/10.6084/m9.figshare.13648166.v1).
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The source record describes an otoscope-image dataset. This repository uses three public images
in a static saved-case bundle. Each case records categorical output from a local AOM feature-analysis
run and a field-of-view overlay; the fixture data is committed in `web/public-cases.json`.

The public interface does not accept uploads or execute inference. The saved outputs deliberately
omit probabilities, thresholds, timings, performance figures, diagnoses, and treatment or referral
recommendations. Private evaluation metrics and operational measurements are intentionally excluded;
the bundle demonstrates review workflow and output traceability, not model performance. Every case is
marked for human review and is not a clinical assessment.

The source images are retained only to render the public workstation screenshot and saved-case
gallery. Do not use them to infer patient identity, attach patient information, or imply endorsement
by the original dataset authors or Figshare.
