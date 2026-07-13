const sampleGrid = document.getElementById("sample-grid");
const decisionSummary = document.getElementById("decision-summary");
const signalList = document.getElementById("signal-list");
const uploadInput = document.getElementById("upload-input");
const caseCanvas = document.getElementById("case-canvas");
const caseCaption = document.getElementById("case-caption");
const signalBars = document.getElementById("signal-bars");

function renderSignals(sample) {
  signalList.innerHTML = "";
  [
    ["Redness ratio", sample.redness_ratio.toFixed(2)],
    ["Texture score", sample.texture_score.toFixed(2)],
    ["Model probability", sample.model_probability.toFixed(2)],
    ["Decision bucket", sample.bucket.replace("_", " ")]
  ].forEach(([term, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = term;
    const dd = document.createElement("dd");
    dd.textContent = value;
    signalList.append(dt, dd);
  });
}

function renderCaseView(imageUrl, payload, label) {
  const ctx = caseCanvas.getContext("2d");
  const img = new Image();
  img.onload = () => {
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, caseCanvas.width, caseCanvas.height);
    ctx.drawImage(img, 0, 0, caseCanvas.width, caseCanvas.height);

    const region = payload.region;
    const scaleX = caseCanvas.width / region.image_width;
    const scaleY = caseCanvas.height / region.image_height;
    const x = region.x0 * scaleX;
    const y = region.y0 * scaleY;
    const width = (region.x1 - region.x0) * scaleX;
    const height = (region.y1 - region.y0) * scaleY;

    ctx.strokeStyle = "#1d4ed8";
    ctx.lineWidth = 3;
    ctx.setLineDash([10, 6]);
    ctx.strokeRect(x, y, width, height);
    ctx.setLineDash([]);

    const tag = "signal region";
    ctx.font = "14px system-ui, sans-serif";
    const tagWidth = ctx.measureText(tag).width + 12;
    const tagY = Math.max(y - 24, 2);
    ctx.fillStyle = "#1d4ed8";
    ctx.fillRect(x, tagY, tagWidth, 22);
    ctx.fillStyle = "#ffffff";
    ctx.fillText(tag, x + 6, tagY + 16);

    caseCaption.textContent =
      `${label} — detected region covers ${(region.coverage * 100).toFixed(1)}% of the frame ` +
      `(synthetic case; no clinical imagery).`;
  };
  img.src = imageUrl;
}

function appendBar(container, label, value, options = {}) {
  const row = document.createElement("div");
  row.className = "bar-row";

  const name = document.createElement("span");
  name.className = "bar-label";
  name.textContent = label;

  const track = document.createElement("div");
  track.className = "bar-track";

  const fill = document.createElement("div");
  fill.className = `bar-fill${options.emphasis ? " bar-fill-emphasis" : ""}`;
  fill.style.width = `${Math.min(Math.max(value, 0), 1) * 100}%`;
  track.appendChild(fill);

  if (typeof options.marker === "number") {
    const marker = document.createElement("div");
    marker.className = "bar-marker";
    marker.style.left = `${Math.min(Math.max(options.marker, 0), 1) * 100}%`;
    marker.title = `decision threshold ${options.marker.toFixed(2)}`;
    track.appendChild(marker);
  }

  const reading = document.createElement("span");
  reading.className = "bar-value";
  reading.textContent = value.toFixed(2);

  row.append(name, track, reading);
  container.appendChild(row);
}

function renderSignalBars(payload) {
  signalBars.innerHTML = "";
  appendBar(signalBars, "Redness ratio", payload.signals.redness_ratio);
  appendBar(signalBars, "Texture score", payload.signals.texture_score);
  appendBar(signalBars, "Calibrated probability", payload.model.calibrated_probability, {
    marker: payload.decision.threshold_used,
    emphasis: true
  });

  const legend = document.createElement("p");
  legend.className = "bar-legend";
  legend.textContent =
    `Tick marks the decision threshold applied to this case ` +
    `(${payload.decision.threshold_used.toFixed(2)}) from the calibrated decision config.`;
  signalBars.appendChild(legend);
}

function selectSample(sample) {
  decisionSummary.textContent =
    `${sample.label}: ${sample.bucket.replace("_", " ")} based on combined visual signals and calibrated model output.`;
  renderSignals(sample);
}

async function analyzeFile(file, label = file.name) {
  const formData = new FormData();
  formData.append("image", file);
  const response = await fetch("/v1/analyze", { method: "POST", body: formData });
  const payload = await response.json();
  selectSample({
    label,
    bucket: payload.decision.bucket,
    redness_ratio: payload.signals.redness_ratio,
    texture_score: payload.signals.texture_score,
    model_probability: payload.model.calibrated_probability
  });
  renderCaseView(URL.createObjectURL(file), payload, label);
  renderSignalBars(payload);
}

async function loadExamples() {
  const response = await fetch("/examples");
  const examples = await response.json();
  sampleGrid.innerHTML = "";
  examples.forEach((example) => {
    const article = document.createElement("article");
    article.className = "sample-card";
    article.innerHTML = `
      <img src="${example.image_url}" alt="${example.label}">
      <h3>${example.label}</h3>
      <p>${example.description}</p>
    `;
    article.addEventListener("click", async () => {
      const imageResponse = await fetch(example.image_url);
      const blob = await imageResponse.blob();
      const file = new File([blob], `${example.case_id}.png`, { type: "image/png" });
      await analyzeFile(file, example.label);
    });
    sampleGrid.appendChild(article);
  });
}

uploadInput.addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (file) {
    await analyzeFile(file);
  }
});

loadExamples();
