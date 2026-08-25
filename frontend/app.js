// Scholarix Trust Audit — frontend logic.
// No build step, no framework: vanilla fetch() + DOM rendering, on purpose,
// so the whole prototype runs from one `python -m backend.main` command.

const API_BASE = ""; // same-origin, Flask serves both API and static files

const els = {
  ledger: document.getElementById("ledger"),
  authorsLoadedLabel: document.getElementById("authors-loaded-label"),
  tabs: document.getElementById("tabs"),
  views: {
    all: document.getElementById("view-all"),
    worst: document.getElementById("view-worst"),
    detail: document.getElementById("view-detail"),
  },
  authorsBody: document.getElementById("authors-table-body"),
  worstList: document.getElementById("worst-list"),
  detailHeader: document.getElementById("detail-header"),
  detailList: document.getElementById("detail-list"),
  backBtn: document.getElementById("back-btn"),
};

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

// Highlights known hedge/definitive phrases inside a reasoning string.
// Works on the escaped HTML so we never inject unsafe content.
function highlightReasoning(text, hedgePhrases, definitivePhrases) {
  let escaped = escapeHtml(text);
  const all = [
    ...(hedgePhrases || []).map((p) => ({ phrase: p, cls: "" })),
    ...(definitivePhrases || []).map((p) => ({ phrase: p, cls: "definitive" })),
  ].sort((a, b) => b.phrase.length - a.phrase.length); // longest first avoids partial overlaps

  all.forEach(({ phrase, cls }) => {
    const escapedPhrase = escapeHtml(phrase);
    const re = new RegExp(escapedPhrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "ig");
    escaped = escaped.replace(re, (match) => `<mark class="${cls}">${match}</mark>`);
  });
  return escaped;
}

function pctClass(pct) {
  if (pct >= 50) return "high";
  if (pct >= 20) return "mid";
  return "low";
}

function renderLedger(summary) {
  els.ledger.innerHTML = `
    <div class="ledger-item">
      <span class="ledger-value">${summary.total_records}</span>
      <span class="ledger-label">Claims Reviewed</span>
      <span class="ledger-sub">across ${summary.authors_count} researchers</span>
    </div>
    <div class="ledger-item">
      <span class="ledger-value consistent">${summary.consistent}</span>
      <span class="ledger-label">Consistent</span>
      <span class="ledger-sub">${summary.consistent_pct}% of claims</span>
    </div>
    <div class="ledger-item">
      <span class="ledger-value overstated">${summary.overstated}</span>
      <span class="ledger-label">Overstated Confidence</span>
      <span class="ledger-sub">avg correction −${summary.avg_adjustment_when_flagged} pts</span>
    </div>
    <div class="ledger-item">
      <span class="ledger-value understated">${summary.understated}</span>
      <span class="ledger-label">Understated Confidence</span>
      <span class="ledger-sub">${summary.understated_pct}% of claims</span>
    </div>
  `;
}

function renderAuthorsTable(authors) {
  if (!authors.length) {
    els.authorsBody.innerHTML = `<tr><td colspan="5" class="empty-state">No researcher data found.</td></tr>`;
    return;
  }
  els.authorsBody.innerHTML = authors
    .map(
      (a) => `
      <tr data-author-id="${escapeHtml(a.id)}">
        <td>
          <div class="researcher-name">${escapeHtml(a.name)}</div>
        </td>
        <td class="researcher-affil">${escapeHtml(a.affiliation || "—")}</td>
        <td class="num">${a.total_records}</td>
        <td class="num">${a.overstated}</td>
        <td class="num"><span class="pct-pill ${pctClass(a.overstated_pct)}">${a.overstated_pct}%</span></td>
      </tr>
    `
    )
    .join("");

  els.authorsBody.querySelectorAll("tr[data-author-id]").forEach((row) => {
    row.addEventListener("click", () => openAuthorDetail(row.dataset.authorId));
  });
}

function evidenceCardHtml(record, authorName) {
  const isOverstated = record.verdict === "Overstated Confidence";
  const isUnderstated = record.verdict === "Understated Confidence";
  const verdictClass = isOverstated ? "overstated" : isUnderstated ? "understated" : "consistent";

  const scoreBlock = record.verdict === "Consistent"
    ? `<div class="score-block"><span class="score-original">${record.original_score}</span></div>`
    : `<div class="score-block">
         <span class="score-original struck">${record.original_score}</span>
         <span class="score-arrow">&rarr;</span>
         <span class="score-adjusted ${isUnderstated ? "understated" : ""}">${record.adjusted_score}</span>
       </div>`;

  return `
    <div class="evidence-card">
      <div class="evidence-card-head">
        <span>${authorName ? `<span class="author-tag">${escapeHtml(authorName)}</span> · ` : ""}${escapeHtml(record.category || "Unknown")}</span>
        <span>relevance score audit</span>
      </div>
      <div class="evidence-card-body">
        ${record.url ? `<span class="evidence-url">${escapeHtml(record.url)}</span>` : ""}
        ${record.snippet ? `<p class="evidence-snippet">"${escapeHtml(record.snippet)}"</p>` : ""}
        <div class="reasoning-block">${highlightReasoning(record.reasoning, record.hedge_phrases_found, record.definitive_phrases_found)}</div>
        <div class="correction-row">
          ${scoreBlock}
          <span class="verdict-tag ${verdictClass}">${escapeHtml(record.verdict)}${record.severity && record.severity !== "None" ? " · " + record.severity : ""}</span>
        </div>
        <p class="explanation-text">${escapeHtml(record.explanation)}</p>
      </div>
    </div>
  `;
}

function renderWorstOffenders(worst) {
  if (!worst.length) {
    els.worstList.innerHTML = `<div class="empty-state">No overstated records found.</div>`;
    return;
  }
  els.worstList.innerHTML = worst.map((r) => evidenceCardHtml(r, r.author_name)).join("");
}

async function openAuthorDetail(authorId) {
  setActiveView("detail");
  els.detailHeader.innerHTML = `<p class="section-note">Loading…</p>`;
  els.detailList.innerHTML = "";

  const res = await fetch(`${API_BASE}/api/authors/${encodeURIComponent(authorId)}`);
  if (!res.ok) {
    els.detailHeader.innerHTML = `<p class="section-note">Could not load this researcher's record.</p>`;
    return;
  }
  const data = await res.json();
  const s = data.summary;

  els.detailHeader.innerHTML = `
    <h2>${escapeHtml(data.name)}</h2>
    <p class="affil">${escapeHtml(data.affiliation || "Affiliation not listed")}</p>
    <div class="detail-stats">
      <span><b>${s.total_records}</b> claims reviewed</span>
      <span><b>${s.overstated}</b> overstated</span>
      <span><b>${s.understated}</b> understated</span>
      <span><b>${data.publications_count}</b> publications on record</span>
    </div>
  `;

  const sorted = [...data.records].sort((a, b) => {
    const gapA = Math.abs(a.original_score - a.adjusted_score);
    const gapB = Math.abs(b.original_score - b.adjusted_score);
    return gapB - gapA;
  });

  els.detailList.innerHTML = sorted.map((r) => evidenceCardHtml(r)).join("");
}

function setActiveView(view) {
  Object.entries(els.views).forEach(([key, el]) => {
    el.classList.toggle("active", key === view);
  });
  els.tabs.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === view);
  });
}

els.tabs.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => setActiveView(btn.dataset.view));
});

els.backBtn.addEventListener("click", () => setActiveView("all"));

async function init() {
  try {
    const [summaryRes, authorsRes] = await Promise.all([
      fetch(`${API_BASE}/api/summary`),
      fetch(`${API_BASE}/api/authors`),
    ]);

    if (!summaryRes.ok || !authorsRes.ok) throw new Error("API request failed");

    const summary = await summaryRes.json();
    const authorsData = await authorsRes.json();

    els.authorsLoadedLabel.textContent = `${authorsData.count} researchers · ${summary.total_records} claims audited`;
    renderLedger(summary);
    renderAuthorsTable(authorsData.authors);
    renderWorstOffenders(summary.worst_offenders || []);
  } catch (err) {
    els.authorsLoadedLabel.textContent = "failed to load data";
    els.ledger.innerHTML = `<div class="empty-state" style="grid-column: 1 / -1;">
      Could not reach the API. Make sure the backend is running (see README) and refresh this page.
    </div>`;
    console.error(err);
  }
}

init();
