const caseGrid = document.getElementById("case-grid");
const caseCanvas = document.getElementById("case-canvas");
const caseCaption = document.getElementById("case-caption");
const signalList = document.getElementById("signal-list");
const reviewNote = document.getElementById("review-note");
const caseProvenance = document.getElementById("case-provenance");

function renderSignals(caseData) {
  signalList.innerHTML = "";
  caseData.signals.forEach(({ label, state }) => {
    const row = document.createElement("div");
    row.className = "signal-row";
    const term = document.createElement("dt");
    term.textContent = label;
    const value = document.createElement("dd");
    value.textContent = state === "recorded signal" ? "Recorded signal" : "Not recorded";
    value.className = state === "recorded signal" ? "signal-present" : "signal-absent";
    row.append(term, value);
    signalList.appendChild(row);
  });
}

function renderCaseView(caseData) {
  const context = caseCanvas.getContext("2d");
  const image = new Image();
  image.onload = () => {
    const size = Math.min(image.naturalWidth, image.naturalHeight);
    caseCanvas.width = size;
    caseCanvas.height = size;
    context.clearRect(0, 0, size, size);
    context.drawImage(image, 0, 0, size, size);

    const { x, y, width, height } = caseData.roi;
    context.strokeStyle = "#9a3d2f";
    context.lineWidth = Math.max(3, size / 160);
    context.setLineDash([size / 42, size / 70]);
    context.strokeRect(x * size, y * size, width * size, height * size);
    context.setLineDash([]);

    const label = "field of view";
    context.font = `${Math.max(14, size / 32)}px system-ui, sans-serif`;
    const labelWidth = context.measureText(label).width + 16;
    const labelY = Math.max(y * size - 28, 4);
    context.fillStyle = "#9a3d2f";
    context.fillRect(x * size, labelY, labelWidth, 24);
    context.fillStyle = "#ffffff";
    context.fillText(label, x * size + 8, labelY + 17);
  };
  image.src = caseData.image_url;
  caseCaption.textContent =
    `${caseData.title}: saved field-of-view overlay from the recorded local pipeline run.`;
}

function selectCase(caseData, selector) {
  document.querySelectorAll(".case-selector").forEach((button) => {
    button.classList.toggle("is-selected", button === selector);
    button.setAttribute("aria-pressed", String(button === selector));
  });
  renderCaseView(caseData);
  renderSignals(caseData);
  const disagreement = caseData.detector_disagreement
    ? "Detector disagreement is present. "
    : "No detector disagreement is recorded. ";
  reviewNote.innerHTML = `<strong>Human review required.</strong> ${disagreement}${caseData.review_note} ` +
    "This is recorded local pipeline output on a public reference image, not a clinical assessment.";
  caseProvenance.textContent = `Source: ${caseData.source}. License: ${caseData.license}.`;
}

function renderCaseSelectors(cases) {
  caseGrid.innerHTML = "";
  cases.forEach((caseData, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "case-selector";
    button.setAttribute("aria-pressed", "false");
    button.innerHTML = `
      <img src="${caseData.image_url}" alt="${caseData.title} public otoscopic reference image">
      <span>${caseData.title}</span>
      <small>Saved output</small>
    `;
    button.addEventListener("click", () => selectCase(caseData, button));
    caseGrid.appendChild(button);
    if (index === 0) {
      selectCase(caseData, button);
    }
  });
}

async function loadPublicCases() {
  const response = await fetch("./public-cases.json");
  if (!response.ok) {
    throw new Error("Unable to load recorded public cases.");
  }
  const { cases } = await response.json();
  renderCaseSelectors(cases);
}

loadPublicCases().catch((error) => {
  caseGrid.textContent = error.message;
});
