const API = "http://localhost:8000/api";
let selectedFile = null;

/* ── Helpers ── */
function showToast(msg, type) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = "toast " + type;
  t.style.display = "block";
  setTimeout(() => (t.style.display = "none"), 3500);
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 120) + "px";
}

function fileIcon(name) {
  const ext = (name || "").split(".").pop().toLowerCase();
  if (ext === "pdf")                          return "ti-file-type-pdf";
  if (ext === "docx")                         return "ti-file-type-doc";
  if (["png","jpg","jpeg","webp"].includes(ext)) return "ti-photo";
  return "ti-file-text";
}

/* ── File selection ── */
const dropZone  = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");

document.getElementById("browse-btn").addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", e => {
  e.preventDefault();
  dropZone.style.background = "#f0effe";
});

dropZone.addEventListener("dragleave", () => {
  dropZone.style.background = "";
});

dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.style.background = "";
  if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) setFile(fileInput.files[0]);
});

function setFile(f) {
  selectedFile = f;
  document.getElementById("selected-name").textContent = f.name;
  document.getElementById("selected-preview").style.display = "flex";
  document.getElementById("upload-btn").disabled = false;
}

function clearFile() {
  selectedFile = null;
  fileInput.value = "";
  document.getElementById("selected-preview").style.display = "none";
  document.getElementById("upload-btn").disabled = true;
}

document.getElementById("clear-file-btn").addEventListener("click", clearFile);

/* ── Upload ── */
async function uploadFile() {
  if (!selectedFile) return;

  const btn = document.getElementById("upload-btn");
  const pb  = document.getElementById("progress-bar");
  const pf  = document.getElementById("progress-fill");

  btn.disabled = true;
  btn.innerHTML = '<i class="ti ti-loader-2"></i> Uploading…';
  pb.style.display = "block";
  pf.style.width = "30%";

  const form = new FormData();
  form.append("file", selectedFile);

  try {
    pf.style.width = "70%";
    const res  = await fetch(`${API}/upload`, { method: "POST", body: form });
    const data = await res.json();
    pf.style.width = "100%";
    if (!res.ok) throw new Error(data.detail || "Upload failed");
    showToast(`✓ ${data.filename} — ${data.chunks_stored} chunks stored`, "success");
    clearFile();
    loadDocuments();
  } catch (e) {
    showToast("Upload failed: " + e.message, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="ti ti-upload"></i> Upload';
    setTimeout(() => {
      pb.style.display = "none";
      pf.style.width = "0%";
    }, 700);
  }
}

document.getElementById("upload-btn").addEventListener("click", uploadFile);

/* ── Document list ── */
async function loadDocuments() {
  try {
    const res  = await fetch(`${API}/documents`);
    const data = await res.json();
    const list  = document.getElementById("doc-list");
    const count = document.getElementById("doc-count");

    if (!data.documents || data.documents.length === 0) {
      list.innerHTML = '<div class="doc-empty">No documents yet.</div>';
      count.textContent = "";
      return;
    }

    count.textContent = `(${data.total})`;
    list.innerHTML = data.documents.map(d => `
      <div class="doc-item" id="doc-${CSS.escape(d)}">
        <i class="ti ${fileIcon(d)}"></i>
        <span title="${d}">${d}</span>
        <div class="doc-actions">
          <button class="doc-btn select-btn" onclick="selectDoc('${d}')" title="Select">
            <i class="ti ti-check"></i>
          </button>
          <button class="doc-btn delete-btn" onclick="deleteDoc('${d}')" title="Delete">
            <i class="ti ti-trash"></i>
          </button>
        </div>
      </div>
    `).join("");
  } catch (_) {}
}

let activeDoc = null;

function selectDoc(name) {
  if (activeDoc === name) {
    activeDoc = null;
    document.querySelectorAll(".doc-item").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".select-btn").forEach(el => el.classList.remove("selected"));
    showToast("Deselected document", "success");
    return;
  }

  activeDoc = name;
  document.querySelectorAll(".doc-item").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".select-btn").forEach(el => el.classList.remove("selected"));

  const item = document.getElementById(`doc-${CSS.escape(name)}`);
  if (item) {
    item.classList.add("active");
    item.querySelector(".select-btn").classList.add("selected");
  }
  showToast(`✓ Focused on "${name}"`, "success");
}

async function deleteDoc(name) {
  if (!confirm(`Delete "${name}" from the knowledge base?`)) return;
  try {
    const res = await fetch(`${API}/documents/${encodeURIComponent(name)}`, {
      method: "DELETE"
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Delete failed");
    }
    showToast(`✓ "${name}" deleted`, "success");
    if (activeDoc === name) activeDoc = null;
    loadDocuments();
  } catch (e) {
    showToast("Delete failed: " + e.message, "error");
  }
}

document.getElementById("refresh-btn").addEventListener("click", loadDocuments);



/* ── Chat ── */
function scrollToBottom() {
  const msgs = document.getElementById("messages");
  msgs.scrollTop = msgs.scrollHeight;
}

function removeWelcome() {
  const w = document.getElementById("messages").querySelector(".welcome");
  if (w) w.remove();
}

function addMessage(role, text, sources) {
  removeWelcome();
  const msgs = document.getElementById("messages");

  let sourcesHTML = "";
  if (sources && sources.length > 0) {
    sourcesHTML = `<div class="sources">` + sources.map(s => `
      <div class="source-chip">
        <i class="ti ${fileIcon(s.doc_name)}"></i>
        <div>
          <div class="source-name">${s.doc_name}</div>
          <div class="source-score">Relevance: ${(s.score * 100).toFixed(0)}%</div>
          <div class="source-excerpt">${s.content}</div>
        </div>
      </div>
    `).join("") + `</div>`;
  }

  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerHTML = `
    <div class="avatar ${role}">${role === "ai" ? "AI" : "You"}</div>
    <div class="msg-content">
      <div class="bubble">${text.replace(/\n/g, "<br>")}</div>
      ${sourcesHTML}
    </div>
  `;

  msgs.appendChild(div);
  scrollToBottom();
}

function addThinking() {
  removeWelcome();
  const msgs = document.getElementById("messages");
  const div  = document.createElement("div");
  div.className = "message ai";
  div.id = "thinking-msg";
  div.innerHTML = `
    <div class="avatar ai">AI</div>
    <div class="msg-content">
      <div class="thinking">
        <div class="dots">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        Thinking…
      </div>
    </div>
  `;
  msgs.appendChild(div);
  scrollToBottom();
}

function removeThinking() {
  const t = document.getElementById("thinking-msg");
  if (t) t.remove();
}

function clearChat() {
  document.getElementById("messages").innerHTML = `
    <div class="welcome">
      <div class="welcome-icon"><i class="ti ti-book-2"></i></div>
      <h3>Ready to answer from your docs</h3>
      <p>Upload one or more documents on the left,<br />then ask questions about their content.</p>
    </div>
  `;
}

document.getElementById("clear-chat-btn").addEventListener("click", clearChat);

/* ── Send query ── */
async function sendQuery() {
  const input = document.getElementById("query");
  const btn   = document.getElementById("send-btn");
  const q     = input.value.trim();
  if (!q) return;

  addMessage("user", q);
  input.value = "";
  input.style.height = "auto";
  btn.disabled = true;
  addThinking();

  try {
    const res  = await fetch(`${API}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    });
    const data = await res.json();
    removeThinking();
    if (!res.ok) throw new Error(data.detail || "Query failed");
    addMessage("ai", data.answer, data.sources);
  } catch (e) {
    removeThinking();
    addMessage("ai", "Something went wrong: " + e.message);
  } finally {
    btn.disabled = false;
  }
}

document.getElementById("send-btn").addEventListener("click", sendQuery);

document.getElementById("query").addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendQuery();
  }
});

document.getElementById("query").addEventListener("input", function () {
  autoResize(this);
});

/* ── Init ── */
loadDocuments();