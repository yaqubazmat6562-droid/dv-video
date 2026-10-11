const API = "";

let currentFileId = null;
let currentDuration = 0;

// ==================== UPLOAD ====================
document.getElementById("file-input").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  // فائل سائز چیک (100 MB limit)
  const sizeMB = file.size / (1024 * 1024);
  if (sizeMB > 100) {
    if (!confirm(`File size is ${sizeMB.toFixed(1)} MB. Large files may be slow. Continue?`)) {
      return;
    }
  }

  showLoading(`Uploading (${sizeMB.toFixed(1)} MB)...`);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API}/api/upload`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    currentFileId = data.file_id;
    currentDuration = data.duration;

    document.getElementById("file-name").textContent = data.filename;
    document.getElementById("file-duration").textContent = data.duration.toFixed(2);

    document.getElementById("preview-video").src = data.url;
    document.getElementById("preview-section").classList.remove("hidden");
    document.getElementById("upload-info").classList.remove("hidden");
    document.getElementById("actions-section").classList.remove("hidden");
    document.getElementById("result-section").classList.add("hidden");

    document.getElementById("trim-end").value = data.duration.toFixed(1);

    hideLoading();
  } catch (err) {
    hideLoading();
    alert("Upload failed: " + err.message);
  }
});

// ==================== PANEL ====================
function showPanel(name) {
  document.querySelectorAll(".panel").forEach(p => p.classList.add("hidden"));
  const panel = document.getElementById(`panel-${name}`);
  if (panel) panel.classList.remove("hidden");
}

// Speed slider
document.getElementById("speed-slider").addEventListener("input", (e) => {
  document.getElementById("speed-value").textContent = e.target.value;
});

// ==================== TRIM ====================
async function applyTrim() {
  if (!currentFileId) return;
  const start = parseFloat(document.getElementById("trim-start").value);
  const end = parseFloat(document.getElementById("trim-end").value);

  if (end <= start) {
    alert("End must be greater than Start");
    return;
  }

  showLoading("Trimming...");
  try {
    const res = await fetch(`${API}/api/trim`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        file_id: currentFileId,
        start: start,
        end: end,
      }),
    });
    const data = await res.json();
    showResult(data.url);
  } catch (err) {
    hideLoading();
    alert("Failed: " + err.message);
  }
}

// ==================== SPEED ====================
async function applySpeed() {
  if (!currentFileId) return;
  const speed = parseFloat(document.getElementById("speed-slider").value);

  showLoading("Changing speed...");
  try {
    const res = await fetch(`${API}/api/speed`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        file_id: currentFileId,
        speed: speed,
      }),
    });
    const data = await res.json();
    showResult(data.url);
  } catch (err) {
    hideLoading();
    alert("Failed: " + err.message);
  }
}

// ==================== FILTER ====================
async function applyFilter() {
  if (!currentFileId) return;
  const preset = document.getElementById("filter-preset").value;

  showLoading("Applying filter...");
  try {
    const res = await fetch(`${API}/api/filter`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        file_id: currentFileId,
        preset: preset,
      }),
    });
    const data = await res.json();
    showResult(data.url);
  } catch (err) {
    hideLoading();
    alert("Failed: " + err.message);
  }
}

// ==================== TEXT ====================
async function applyText() {
  if (!currentFileId) return;
  const text = document.getElementById("text-input").value.trim();
  if (!text) {
    alert("Please enter text");
    return;
  }

  showLoading("Adding text...");
  try {
    const res = await fetch(`${API}/api/text`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        file_id: currentFileId,
        text: text,
        position: document.getElementById("text-pos").value,
        color: document.getElementById("text-color").value,
        font_size: 48,
      }),
    });
    const data = await res.json();
    showResult(data.url);
  } catch (err) {
    hideLoading();
    alert("Failed: " + err.message);
  }
}

// ==================== RESULT ====================
function showResult(url) {
  hideLoading();
  const resultSection = document.getElementById("result-section");
  resultSection.classList.remove("hidden");

  const video = document.getElementById("result-video");
  video.src = url;

  const dl = document.getElementById("download-btn");
  dl.href = url;
  dl.download = url.split("/").pop();

  resultSection.scrollIntoView({ behavior: "smooth" });
}

// ==================== LOADING ====================
function showLoading(text = "Processing...") {
  document.getElementById("loading-text").textContent = text;
  document.getElementById("loading").classList.remove("hidden");
}

function hideLoading() {
  document.getElementById("loading").classList.add("hidden");
}

function toggleMenu() {
  alert("🚀 DV Studio Mobile\n\n1. Upload\n2. Choose Action\n3. Download");
}