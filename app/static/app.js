/* ============================================================
   AI Research Assistant – Client-Side Logic
   ============================================================ */

const STEPS = [
  { key: "planning",      label: "Planning research tasks" },
  { key: "searching",     label: "Searching the web" },
  { key: "deduplicating", label: "Removing duplicates" },
  { key: "summarising",   label: "Summarising findings" },
  { key: "writing",       label: "Writing the report" },
  { key: "reviewing",     label: "Reviewing the draft" },
  { key: "completed",     label: "Report generated" },
];

let currentJobId = null;
let pollTimer    = null;

/* ── Bootstrap pipeline HTML ── */
function renderPipeline() {
  const el = document.getElementById("pipeline");
  el.innerHTML = STEPS.map((s, i) => `
    <div class="step" id="step-${s.key}" data-index="${i}">
      <div class="step-circle"><span class="step-number">${i + 1}</span></div>
      <span class="step-label">${s.label}</span>
    </div>
  `).join("");
}

/* ── Update step states ── */
function setActiveStep(stageKey) {
  const idx = STEPS.findIndex(s => s.key === stageKey);
  STEPS.forEach((s, i) => {
    const el = document.getElementById(`step-${s.key}`);
    el.classList.remove("active", "done");
    if (i < idx)       el.classList.add("done");
    else if (i === idx) el.classList.add("active");
  });
}

/* ── Show / hide sections ── */
function show(id)  { document.getElementById(id).classList.remove("hidden"); }
function hide(id)  { document.getElementById(id).classList.add("hidden"); }

/* ── Start a research job ── */
async function startResearch() {
  const input = document.getElementById("topic-input");
  const topic = input.value.trim();
  if (!topic) { input.focus(); return; }

  // Disable UI
  document.getElementById("start-btn").disabled = true;
  input.disabled = true;

  // Show progress
  renderPipeline();
  document.getElementById("topic-badge").textContent = topic;
  show("progress-section");
  hide("result-section");
  hide("error-section");
  document.getElementById("status-message").textContent = "Starting…";

  try {
    const res = await fetch("/api/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    currentJobId = data.job_id;
    pollProgress();
  } catch (err) {
    showError(err.message);
  }
}

/* ── Poll for progress ── */
function pollProgress() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(async () => {
    try {
      const res = await fetch(`/api/research/${currentJobId}`);
      if (!res.ok) throw new Error("Lost connection to server");
      const job = await res.json();

      // Map stage — handle "written (revision N)" and "reviewed (score N)" etc.
      let stage = job.stage || "planning";
      if (stage.startsWith("written"))  stage = "writing";
      if (stage.startsWith("reviewed")) stage = "reviewing";

      setActiveStep(stage);
      document.getElementById("status-message").textContent =
        job.stage_label || stage;

      if (job.status === "completed") {
        clearInterval(pollTimer);
        // Mark all done
        STEPS.forEach(s => {
          document.getElementById(`step-${s.key}`).classList.remove("active");
          document.getElementById(`step-${s.key}`).classList.add("done");
        });
        document.getElementById("status-message").textContent = "";
        showResult(job);
      } else if (job.status === "failed") {
        clearInterval(pollTimer);
        showError(job.error || "Unknown error");
      }
    } catch (err) {
      clearInterval(pollTimer);
      showError(err.message);
    }
  }, 1500);
}

/* ── Display results ── */
function showResult(job) {
  const meta = document.getElementById("result-meta");
  meta.innerHTML = `
    <span class="meta-chip"><strong>${job.sources_used}</strong> sources</span>
    <span class="meta-chip"><strong>${job.duplicates_removed}</strong> duplicates removed</span>
    <span class="meta-chip"><strong>${job.revisions}</strong> revision(s)</span>
    <span class="meta-chip">Score: <strong>${job.review?.score ?? "—"}</strong>/10</span>
  `;
  document.getElementById("report-body").textContent = job.report || "";
  show("result-section");

  // Re-enable input
  document.getElementById("start-btn").disabled = false;
  document.getElementById("topic-input").disabled = false;
}

/* ── Download helper ── */
function downloadReport(fmt) {
  if (!currentJobId) return;
  window.open(`/api/research/${currentJobId}/download/${fmt}`, "_blank");
}

/* ── Show error ── */
function showError(msg) {
  document.getElementById("error-message").textContent = msg;
  show("error-section");
  document.getElementById("start-btn").disabled = false;
  document.getElementById("topic-input").disabled = false;
}

/* ── Reset ── */
function resetUI() {
  hide("progress-section");
  hide("result-section");
  hide("error-section");
  document.getElementById("topic-input").value = "";
  document.getElementById("topic-input").disabled = false;
  document.getElementById("start-btn").disabled = false;
  currentJobId = null;
}

/* ── Enter key support ── */
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("topic-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") startResearch();
  });
});
