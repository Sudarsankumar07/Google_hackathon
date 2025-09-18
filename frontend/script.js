// Always use the backend URL; change if your backend runs elsewhere
const API_BASE = "http://localhost:8000";

const domainSelect = document.getElementById("domain-select");
const loadModelBtn = document.getElementById("load-model-btn");
const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const uploadStatus = document.getElementById("upload-status");
const docList = document.getElementById("doc-list");
const chatArea = document.getElementById("chat-area");
const sendBtn = document.getElementById("send-btn");
const questionInput = document.getElementById("question-input");
let uploadedDocs = []; // {doc_id, name, domain}

loadModelBtn.addEventListener("click", async () => {
  const domain = domainSelect.value;
  loadModelBtn.disabled = true;
  loadModelBtn.textContent = "Loading...";
  try {
    await axios.post(`${API_BASE}/load-model`, { domain });
    alert("Model loaded for " + domain);
  } catch (e) {
    alert("Load model failed: " + (e?.response?.data?.detail || e.message));
  } finally {
    loadModelBtn.disabled = false;
    loadModelBtn.textContent = "Load Model";
  }
});

dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", (e) => { dropZone.classList.remove("dragover"); });
dropZone.addEventListener("drop", async (e) => {
  e.preventDefault(); dropZone.classList.remove("dragover");
  const f = e.dataTransfer.files?.[0];
  if (f) await uploadFile(f);
});

fileInput.addEventListener("change", async (e) => {
  const f = e.target.files?.[0];
  if (f) await uploadFile(f);
});

async function uploadFile(file) {
  uploadStatus.textContent = "Uploading...";
  const domain = domainSelect.value;
  const form = new FormData();
  form.append("file", file);
  form.append("domain", domain);
  try {
    const res = await axios.post(`${API_BASE}/upload`, form, { headers: {"Content-Type":"multipart/form-data"}});
    uploadedDocs.push({doc_id: res.data.doc_id, name: file.name, domain});
    renderDocList();
    uploadStatus.textContent = "Uploaded: " + file.name;
  } catch (e) {
    uploadStatus.textContent = "Upload failed";
    console.error(e);
  }
}

function renderDocList(){
  docList.innerHTML = uploadedDocs.map(d => `<li class="mb-2"><strong>${d.name}</strong> <em class="text-xs text-gray-500">[${d.domain}]</em> <button data-id="${d.doc_id}" class="ml-2 text-blue-600 text-sm">Ask</button></li>`).join("");
  docList.querySelectorAll("button").forEach(b => {
    b.addEventListener("click", () => { questionInput.value = `Please summarize this document (id: ${b.dataset.id})`; });
  });
}

sendBtn.addEventListener("click", async () => {
  const question = questionInput.value.trim();
  if (!question) return;
  const domain = domainSelect.value;
  const doc = uploadedDocs.length ? uploadedDocs[uploadedDocs.length-1] : null;
  chatArea.innerHTML += `<div class="chat-bubble user">${question}</div>`;
  chatArea.scrollTop = chatArea.scrollHeight;
  sendBtn.disabled = true;
  try {
    const payload = { question, domain, doc_id: doc ? doc.doc_id : undefined };
    const res = await axios.post(`${API_BASE}/query`, payload);
    const summary = res.data.summary || res.data;
    chatArea.innerHTML += `<div class="chat-bubble bot">${escapeHtml(summary)}</div>`;
    chatArea.scrollTop = chatArea.scrollHeight;
  } catch (e) {
    chatArea.innerHTML += `<div class="chat-bubble bot">Error: ${e?.response?.data?.detail || e.message}</div>`;
  } finally {
    sendBtn.disabled = false;
  }
});

function escapeHtml(text){
  if (!text) return "";
  return text.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll("\n","<br/>");
}
