/* script.js
   Handles the 4-lane dashboard: image upload, calling the Flask
   /api/detect endpoint, and animating a realistic traffic-light
   signal cycle based on the AI-calculated green times. */

const NUM_LANES = 4;
const laneData = {}; // stores detection result per lane

const laneGrid = document.getElementById("laneGrid");
const junctionView = document.getElementById("junctionView");
const runCycleBtn = document.getElementById("runCycleBtn");
const resetBtn = document.getElementById("resetBtn");
const toast = document.getElementById("toast");

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2500);
}

function buildLaneCards() {
  laneGrid.innerHTML = "";
  for (let i = 1; i <= NUM_LANES; i++) {
    const card = document.createElement("div");
    card.className = "lane-card";
    card.innerHTML = `
      <h3>Lane ${i} <span class="lane-badge" id="badge-${i}">Waiting</span></h3>
      <div class="preview-box" id="preview-${i}"><span>No image selected</span></div>
      <input type="file" accept="image/png, image/jpeg" id="file-${i}">
      <button class="btn btn-primary" onclick="analyzeLane(${i})">🔍 Analyze Lane ${i}</button>
      <div class="result-row" id="result-${i}" style="display:none;"></div>
    `;
    laneGrid.appendChild(card);
  }
}

function buildJunctionView() {
  junctionView.innerHTML = "";
  for (let i = 1; i <= NUM_LANES; i++) {
    const unit = document.createElement("div");
    unit.className = "signal-unit";
    unit.id = `signal-${i}`;
    unit.innerHTML = `
      <div><b>Lane ${i}</b></div>
      <div class="traffic-light">
        <div class="light-dot red" id="red-${i}"></div>
        <div class="light-dot yellow" id="yellow-${i}"></div>
        <div class="light-dot green" id="green-${i}"></div>
      </div>
      <div class="countdown" id="countdown-${i}">--</div>
    `;
    junctionView.appendChild(unit);
  }
  setAllRed();
}

function setAllRed() {
  for (let i = 1; i <= NUM_LANES; i++) {
    document.getElementById(`red-${i}`).classList.add("on");
    document.getElementById(`yellow-${i}`).classList.remove("on");
    document.getElementById(`green-${i}`).classList.remove("on");
    document.getElementById(`signal-${i}`).classList.remove("active-green");
  }
}

// Preview selected image before upload
laneGrid?.addEventListener("change", (e) => {
  if (e.target.tagName === "INPUT" && e.target.type === "file") {
    const laneNum = e.target.id.split("-")[1];
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        document.getElementById(`preview-${laneNum}`).innerHTML =
          `<img src="${ev.target.result}" alt="Lane ${laneNum} preview">`;
      };
      reader.readAsDataURL(file);
    }
  }
});

async function analyzeLane(laneNum) {
  const fileInput = document.getElementById(`file-${laneNum}`);
  const badge = document.getElementById(`badge-${laneNum}`);
  const resultBox = document.getElementById(`result-${laneNum}`);

  if (!fileInput.files.length) {
    showToast(`Please select an image for Lane ${laneNum} first.`);
    return;
  }

  badge.textContent = "Analyzing...";

  const formData = new FormData();
  formData.append("image", fileInput.files[0]);
  formData.append("lane_number", laneNum);

  try {
    const res = await fetch("/api/detect", { method: "POST", body: formData });
    const data = await res.json();

    if (!data.success) {
      showToast(data.error || "Detection failed.");
      badge.textContent = "Error";
      return;
    }

    laneData[laneNum] = data;
    badge.textContent = "Analyzed";

    document.getElementById(`preview-${laneNum}`).innerHTML =
      `<img src="${data.result_image_url}" alt="Detected vehicles">`;

    resultBox.style.display = "flex";
    resultBox.style.flexDirection = "column";
    resultBox.innerHTML = `
      <div class="result-row"><span>Vehicles Detected</span><b>${data.vehicle_count}</b></div>
      <div class="result-row"><span>Density</span><span class="density-tag density-${data.density_level}">${data.density_level}</span></div>
      <div class="result-row"><span>Recommended Green Time</span><b>${data.green_time}s</b></div>
    `;

    checkAllLanesReady();
  } catch (err) {
    showToast("Server error. Is the Flask backend running?");
    badge.textContent = "Error";
  }
}

function checkAllLanesReady() {
  const ready = Object.keys(laneData).length === NUM_LANES;
  runCycleBtn.disabled = !ready;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function runSignalCycle() {
  runCycleBtn.disabled = true;
  let totalVehicles = 0;
  let totalCycleTime = 0;

  for (let i = 1; i <= NUM_LANES; i++) {
    const data = laneData[i];
    totalVehicles += data.vehicle_count;

    setAllRed();

    // YELLOW warning (2s) before this lane's green
    document.getElementById(`red-${i}`).classList.remove("on");
    document.getElementById(`yellow-${i}`).classList.add("on");
    document.getElementById(`countdown-${i}`).textContent = "Get Ready";
    await sleep(1200);
    document.getElementById(`yellow-${i}`).classList.remove("on");

    // GREEN for the calculated duration
    document.getElementById(`green-${i}`).classList.add("on");
    document.getElementById(`signal-${i}`).classList.add("active-green");

    let remaining = data.green_time;
    totalCycleTime += remaining;
    const countdownEl = document.getElementById(`countdown-${i}`);
    countdownEl.textContent = `${remaining}s`;

    await new Promise((resolve) => {
      const interval = setInterval(() => {
        remaining -= 1;
        countdownEl.textContent = `${remaining}s`;
        if (remaining <= 0) {
          clearInterval(interval);
          resolve();
        }
      }, 1000 / 4); // sped up 4x for a quick, engaging live demo
    });

    document.getElementById(`green-${i}`).classList.remove("on");
    document.getElementById(`signal-${i}`).classList.remove("active-green");
    countdownEl.textContent = "Done";
  }

  setAllRed();
  showToast("Signal cycle complete! Saved to database.");

  await fetch("/api/save-cycle", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ total_vehicles: totalVehicles, total_cycle_time: totalCycleTime }),
  });

  runCycleBtn.disabled = false;
}

function resetLanes() {
  for (const key in laneData) delete laneData[key];
  buildLaneCards();
  buildJunctionView();
  runCycleBtn.disabled = true;
  showToast("All lanes reset.");
}

runCycleBtn.addEventListener("click", runSignalCycle);
resetBtn.addEventListener("click", resetLanes);

buildLaneCards();
buildJunctionView();
