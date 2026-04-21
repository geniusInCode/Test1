/* ═══════════════════════════════════════════════════════════════
   Qatar Foundation — Opportunity Management JS
   Handles: List, Create, View, Edit, Delete (US-2.1 to US-2.6)
   ═══════════════════════════════════════════════════════════════ */

let editingId  = null;   // null = create mode, number = edit mode
let deletingId = null;   // ID of the opportunity pending deletion

/* ─── On Page Load ───────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", async () => {
  await loadAdminName();
  await loadOpportunities();
});

/* ─── Load logged-in admin name into navbar ──────────────────── */
async function loadAdminName() {
  try {
    const res  = await fetch("/api/auth/me", { credentials: "include" });
    const data = await res.json();
    if (data.success) {
      const el = document.getElementById("nav-username");
      if (el) el.textContent = `👤 ${data.data.full_name}`;
    } else {
      window.location.href = "/login";
    }
  } catch (_) {}
}

/* ─── US-2.1  LOAD ALL OPPORTUNITIES ────────────────────────── */
async function loadOpportunities() {
  showState("loading");

  try {
    const res  = await fetch("/api/opportunities", { credentials: "include" });
    const data = await res.json();

    if (!data.success) {
      window.location.href = "/login";
      return;
    }

    const grid = document.getElementById("opportunities-grid");
    grid.innerHTML = "";

    if (data.data.length === 0) {
      showState("empty");
      return;
    }

    showState("grid");
    data.data.forEach(opp => grid.appendChild(buildCard(opp)));

  } catch (err) {
    showState("empty");
    console.error("Failed to load opportunities:", err);
  }
}

/* ─── Build opportunity card DOM element ─────────────────────── */
function buildCard(opp) {
  const card = document.createElement("div");
  card.className = "opp-card";
  card.dataset.id = opp.id;

  const maxApp = opp.max_applicants ? `· Max ${opp.max_applicants} applicants` : "";

  card.innerHTML = `
    <span class="opp-card-badge">${escHtml(opp.category)}</span>
    <h3>${escHtml(opp.name)}</h3>
    <div class="opp-card-meta">
      <span>⏱ <strong>Duration:</strong>&nbsp;${escHtml(opp.duration)}</span>
      <span>📅 <strong>Start:</strong>&nbsp;${formatDate(opp.start_date)} ${maxApp}</span>
    </div>
    <p class="opp-card-desc">${escHtml(opp.description)}</p>
    <div class="opp-card-actions">
      <button class="btn btn-view"   onclick="openDetails(${opp.id})">View</button>
      <button class="btn btn-edit"   onclick="openEdit(${opp.id})">Edit</button>
      <button class="btn btn-delete" onclick="openDelete(${opp.id}, '${escHtml(opp.name)}')">Delete</button>
    </div>
  `;
  return card;
}

/* ─── UI State Helper ────────────────────────────────────────── */
function showState(state) {
  document.getElementById("loading-state").classList.add("hidden");
  document.getElementById("empty-state").classList.add("hidden");
  document.getElementById("opportunities-grid").classList.add("hidden");

  if (state === "loading") document.getElementById("loading-state").classList.remove("hidden");
  if (state === "empty")   document.getElementById("empty-state").classList.remove("hidden");
  if (state === "grid")    document.getElementById("opportunities-grid").classList.remove("hidden");
}

/* ═══════════════════════════════════════════════════════════════
   ADD / EDIT MODAL  (US-2.2 and US-2.5)
   ═══════════════════════════════════════════════════════════════ */
function openAddModal() {
  editingId = null;
  clearFormFields();
  document.getElementById("form-modal-title").textContent = "Add New Opportunity";
  document.getElementById("form-submit-btn").textContent  = "Save Opportunity";
  document.getElementById("form-error").classList.add("hidden");
  document.getElementById("form-modal").classList.remove("hidden");
}

async function openEdit(id) {
  try {
    const res  = await fetch(`/api/opportunities/${id}`, { credentials: "include" });
    const data = await res.json();
    if (!data.success) return;

    const opp = data.data;
    editingId  = id;

    document.getElementById("f-name").value        = opp.name;
    document.getElementById("f-category").value    = opp.category;
    document.getElementById("f-duration").value    = opp.duration;
    document.getElementById("f-start-date").value  = opp.start_date;
    document.getElementById("f-max").value         = opp.max_applicants || "";
    document.getElementById("f-description").value = opp.description;
    document.getElementById("f-skills").value      = opp.skills_to_gain;
    document.getElementById("f-future").value      = opp.future_opportunities;

    document.getElementById("form-modal-title").textContent = "Edit Opportunity";
    document.getElementById("form-submit-btn").textContent  = "Update Opportunity";
    document.getElementById("form-error").classList.add("hidden");
    document.getElementById("form-modal").classList.remove("hidden");

  } catch (err) {
    console.error("Failed to load opportunity for editing:", err);
  }
}

function closeFormModal() {
  document.getElementById("form-modal").classList.add("hidden");
  editingId = null;
}

function closeFormModalOnOverlay(e) {
  if (e.target === document.getElementById("form-modal")) closeFormModal();
}

/* ─── US-2.2 / US-2.5  SUBMIT (Create or Update) ────────────── */
async function submitOpportunity() {
  const formError = document.getElementById("form-error");
  formError.classList.add("hidden");

  const payload = {
    name:                 document.getElementById("f-name").value.trim(),
    category:             document.getElementById("f-category").value,
    duration:             document.getElementById("f-duration").value.trim(),
    start_date:           document.getElementById("f-start-date").value,
    description:          document.getElementById("f-description").value.trim(),
    skills_to_gain:       document.getElementById("f-skills").value.trim(),
    future_opportunities: document.getElementById("f-future").value.trim(),
    max_applicants:       document.getElementById("f-max").value || null
  };

  const url    = editingId ? `/api/opportunities/${editingId}` : "/api/opportunities";
  const method = editingId ? "PUT" : "POST";

  const btn = document.getElementById("form-submit-btn");
  btn.disabled    = true;
  btn.textContent = "Saving...";

  try {
    const res  = await fetch(url, {
      method,
      credentials: "include",
      headers:     { "Content-Type": "application/json" },
      body:        JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      closeFormModal();
      await loadOpportunities();      // Refresh cards instantly — no page reload
    } else {
      formError.textContent = data.error || "Validation failed.";
      formError.classList.remove("hidden");
    }
  } catch (err) {
    formError.textContent = "Network error. Please try again.";
    formError.classList.remove("hidden");
  } finally {
    btn.disabled    = false;
    btn.textContent = editingId ? "Update Opportunity" : "Save Opportunity";
  }
}

/* ═══════════════════════════════════════════════════════════════
   DETAILS MODAL  (US-2.4)
   ═══════════════════════════════════════════════════════════════ */
async function openDetails(id) {
  try {
    const res  = await fetch(`/api/opportunities/${id}`, { credentials: "include" });
    const data = await res.json();
    if (!data.success) return;

    const o = data.data;
    document.getElementById("details-content").innerHTML = `
      <div class="detail-row">
        <span class="detail-label">Opportunity Name</span>
        <span class="detail-value">${escHtml(o.name)}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Category</span>
        <span class="detail-value">${escHtml(o.category)}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Duration</span>
        <span class="detail-value">${escHtml(o.duration)}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Start Date</span>
        <span class="detail-value">${formatDate(o.start_date)}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Description</span>
        <span class="detail-value">${escHtml(o.description)}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Skills to Gain</span>
        <span class="detail-value">${escHtml(o.skills_to_gain)}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Future Opportunities</span>
        <span class="detail-value">${escHtml(o.future_opportunities)}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Max Applicants</span>
        <span class="detail-value">${o.max_applicants || "Not specified"}</span>
      </div>
    `;

    document.getElementById("details-modal").classList.remove("hidden");
  } catch (err) {
    console.error("Failed to load opportunity details:", err);
  }
}

function closeDetailsModal() {
  document.getElementById("details-modal").classList.add("hidden");
}
function closeDetailsModalOnOverlay(e) {
  if (e.target === document.getElementById("details-modal")) closeDetailsModal();
}

/* ═══════════════════════════════════════════════════════════════
   DELETE MODAL  (US-2.6)
   ═══════════════════════════════════════════════════════════════ */
function openDelete(id, name) {
  deletingId = id;
  document.getElementById("delete-opp-name").textContent = name;
  document.getElementById("delete-modal").classList.remove("hidden");
}

function closeDeleteModal() {
  document.getElementById("delete-modal").classList.add("hidden");
  deletingId = null;
}
function closeDeleteModalOnOverlay(e) {
  if (e.target === document.getElementById("delete-modal")) closeDeleteModal();
}

async function confirmDelete() {
  if (!deletingId) return;

  const btn = document.getElementById("confirm-delete-btn");
  btn.disabled    = true;
  btn.textContent = "Deleting...";

  try {
    const res  = await fetch(`/api/opportunities/${deletingId}`, {
      method:      "DELETE",
      credentials: "include"
    });
    const data = await res.json();

    if (data.success) {
      closeDeleteModal();
      await loadOpportunities();      // Refresh cards instantly — no page reload
    }
  } catch (err) {
    console.error("Delete failed:", err);
  } finally {
    btn.disabled    = false;
    btn.textContent = "Yes, Delete";
  }
}

/* ─── Logout (called from navbar) ────────────────────────────── */
async function handleLogout() {
  try {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
  } catch (_) {}
  window.location.href = "/login";
}

/* ─── Helpers ────────────────────────────────────────────────── */
function clearFormFields() {
  ["f-name","f-category","f-duration","f-start-date",
   "f-max","f-description","f-skills","f-future"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = "";
  });
}

function escHtml(str) {
  return String(str)
    .replace(/&/g,  "&amp;")
    .replace(/</g,  "&lt;")
    .replace(/>/g,  "&gt;")
    .replace(/"/g,  "&quot;")
    .replace(/'/g,  "&#039;");
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}
