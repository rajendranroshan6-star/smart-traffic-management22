/* history.js
   Fetches stats and logs from the Flask backend and renders
   them into the history/report page. */

const statsGrid = document.getElementById("statsGrid");
const logsBody = document.getElementById("logsBody");
const clearBtn = document.getElementById("clearBtn");
const toast = document.getElementById("toast");

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2500);
}

async function loadStats() {
  const res = await fetch("/api/stats");
  const data = await res.json();
  const stats = data.stats;

  let avgHtml = "";
  stats.per_lane.forEach((lane) => {
    avgHtml += `<div class="stat-card">
        <div class="value">${lane.avg_count.toFixed(1)}</div>
        <div class="label">Avg Vehicles — Lane ${lane.lane_number}</div>
      </div>`;
  });

  statsGrid.innerHTML = `
    <div class="stat-card">
      <div class="value">${stats.total_scans}</div>
      <div class="label">Total AI Scans</div>
    </div>
    <div class="stat-card">
      <div class="value">${stats.total_vehicles}</div>
      <div class="label">Total Vehicles Detected</div>
    </div>
    ${avgHtml}
  `;
}

async function loadLogs() {
  const res = await fetch("/api/logs");
  const data = await res.json();

  if (!data.logs.length) {
    logsBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#94a3b8;">No records yet. Analyze a lane from the Dashboard first.</td></tr>`;
    return;
  }

  logsBody.innerHTML = data.logs
    .map(
      (log, idx) => `
    <tr>
      <td>${idx + 1}</td>
      <td>Lane ${log.lane_number}</td>
      <td>${log.vehicle_count}</td>
      <td><span class="density-tag density-${log.density_level}">${log.density_level}</span></td>
      <td>${log.green_time}s</td>
      <td>${log.timestamp}</td>
    </tr>`
    )
    .join("");
}

async function clearLogs() {
  if (!confirm("This will permanently delete all traffic logs. Continue?")) return;
  await fetch("/api/reset", { method: "POST" });
  showToast("All logs cleared.");
  loadStats();
  loadLogs();
}

clearBtn.addEventListener("click", clearLogs);

loadStats();
loadLogs();
