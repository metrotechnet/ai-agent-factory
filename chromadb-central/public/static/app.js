/* ================================================
   Dataset Editor — App Logic
   ================================================ */
(() => {
  "use strict";

  // ---- Config ----
  const API = window.location.hostname === "localhost"
    ? `http://localhost:${window.location.port || 2000}`
    : "";  // same origin in production

  // ---- DOM refs ----
  const $projectsView  = document.getElementById("project-list-view");
  const $editorView    = document.getElementById("editor-view");
  const $projectsCtr   = document.getElementById("projects-container");
  const $editorTitle   = document.getElementById("editor-title");
  const $tableContainer= document.getElementById("table-container");
  const $status        = document.getElementById("editor-status");
  const $search        = document.getElementById("search-input");
  const $btnUndo       = document.getElementById("btn-undo");
  const $btnRedo       = document.getElementById("btn-redo");
  const $btnSave       = document.getElementById("btn-save");
  const $btnAddRow     = document.getElementById("btn-add-row");
  const $btnDelRows    = document.getElementById("btn-delete-rows");
  const $btnBack       = document.getElementById("btn-back");
  const $btnAddProject = document.getElementById("btn-add-project");
  const $dlgAddProject = document.getElementById("dialog-add-project");
  const $dlgAddFile    = document.getElementById("dialog-add-file");
  const $dlgConfirm    = document.getElementById("dialog-confirm");

  // ---- State ----
  let currentProject = null;
  let currentFile    = null;
  let data           = [];      // current dataset rows
  let columns        = [];      // column names
  let undoStack      = [];
  let redoStack      = [];
  let dirty          = false;
  let selectedRows   = new Set();

  // ================================================
  // API helpers
  // ================================================
  async function api(path, opts = {}) {
    const url = `${API}${path}`;
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json", ...opts.headers },
      ...opts,
    });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`${res.status}: ${body}`);
    }
    return res.json();
  }

  // ================================================
  // Toast
  // ================================================
  function toast(msg, type = "info", ms = 3000) {
    const el = document.getElementById("toast");
    el.textContent = msg;
    el.className = `toast toast-${type}`;
    el.classList.remove("hidden");
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.add("hidden"), ms);
  }

  // ================================================
  // Confirm dialog helper
  // ================================================
  function confirmDialog(title, message) {
    return new Promise(resolve => {
      document.getElementById("confirm-title").textContent = title;
      document.getElementById("confirm-message").textContent = message;
      $dlgConfirm.returnValue = "";
      $dlgConfirm.showModal();
      $dlgConfirm.addEventListener("close", function handler() {
        $dlgConfirm.removeEventListener("close", handler);
        resolve($dlgConfirm.returnValue === "ok");
      });
    });
  }

  // ================================================
  // PROJECT LIST
  // ================================================
  async function loadProjects() {
    try {
      const result = await api("/datasets");
      renderProjects(result.projects);
    } catch (e) {
      toast("Failed to load projects: " + e.message, "error");
    }
  }

  function renderProjects(projects) {
    $projectsCtr.innerHTML = "";
    if (!projects || projects.length === 0) {
      $projectsCtr.innerHTML = `<p style="color:var(--text-muted)">No projects found.</p>`;
      return;
    }
    for (const proj of projects) {
      const card = document.createElement("div");
      card.className = "card";
      const fileItems = (proj.files || []).map(f =>
        `<li>
          <span>📄 ${escapeHtml(f.name)} <small>(${f.records} records)</small></span>
          <button class="btn btn-small" data-edit="${proj.name}/${f.name}">Edit</button>
        </li>`
      ).join("");
      card.innerHTML = `
        <h3>📁 ${escapeHtml(proj.name)}</h3>
        <ul class="file-list">${fileItems || '<li><span style="opacity:.5">No dataset files</span></li>'}</ul>
        <div class="card-actions">
          <button class="btn btn-small" data-add-file="${proj.name}">+ Add File</button>
          <button class="btn btn-small btn-update" data-update="${proj.name}" title="Re-index into ChromaDB">⟳ Update DB</button>
          <button class="btn btn-small btn-danger" data-delete-project="${proj.name}">Delete</button>
        </div>
      `;
      $projectsCtr.appendChild(card);
    }

    // Event delegation
    $projectsCtr.querySelectorAll("[data-edit]").forEach(btn =>
      btn.addEventListener("click", () => {
        const [proj, file] = btn.dataset.edit.split("/");
        openEditor(proj, file);
      })
    );
    $projectsCtr.querySelectorAll("[data-add-file]").forEach(btn =>
      btn.addEventListener("click", () => showAddFileDialog(btn.dataset.addFile))
    );
    $projectsCtr.querySelectorAll("[data-delete-project]").forEach(btn =>
      btn.addEventListener("click", () => deleteProject(btn.dataset.deleteProject))
    );
    $projectsCtr.querySelectorAll("[data-update]").forEach(btn =>
      btn.addEventListener("click", () => updateProject(btn.dataset.update))
    );
  }

  // ---- Create project ----
  $btnAddProject.addEventListener("click", () => {
    document.getElementById("input-project-name").value = "";
    $dlgAddProject.showModal();
  });
  $dlgAddProject.querySelector("form").addEventListener("submit", async (e) => {
    const name = document.getElementById("input-project-name").value.trim();
    if (!name) return;
    try {
      await api("/datasets/" + encodeURIComponent(name), { method: "POST" });
      toast(`Project "${name}" created`, "success");
      loadProjects();
    } catch (err) {
      toast("Error: " + err.message, "error");
    }
  });

  // ---- Add file to project ----
  let _addFileProject = null;
  function showAddFileDialog(proj) {
    _addFileProject = proj;
    document.getElementById("input-file-name").value = "";
    $dlgAddFile.showModal();
  }
  $dlgAddFile.querySelector("form").addEventListener("submit", async () => {
    let fname = document.getElementById("input-file-name").value.trim();
    if (!fname) return;
    if (!fname.endsWith(".json")) fname += ".json";
    try {
      await api(`/datasets/${encodeURIComponent(_addFileProject)}/${encodeURIComponent(fname)}`, {
        method: "PUT",
        body: JSON.stringify([]),
      });
      toast(`File "${fname}" created`, "success");
      loadProjects();
    } catch (err) {
      toast("Error: " + err.message, "error");
    }
  });

  // ---- Delete project ----
  async function deleteProject(name) {
    const ok = await confirmDialog("Delete Project", `Delete project "${name}" and all its dataset files?`);
    if (!ok) return;
    try {
      await api("/datasets/" + encodeURIComponent(name), { method: "DELETE" });
      toast(`Project "${name}" deleted`, "success");
      loadProjects();
    } catch (err) {
      toast("Error: " + err.message, "error");
    }
  }

  // ---- Update project (re-index) ----
  async function updateProject(name) {
    toast(`Triggering re-index for "${name}"...`, "info", 5000);
    try {
      const result = await api(`/datasets/${encodeURIComponent(name)}/reindex`, { method: "POST" });
      toast(`Re-index complete: ${result.indexed} documents indexed`, "success", 5000);
    } catch (err) {
      toast("Re-index error: " + err.message, "error", 5000);
    }
  }

  // ================================================
  // EDITOR
  // ================================================
  async function openEditor(project, file) {
    currentProject = project;
    currentFile = file;
    undoStack = [];
    redoStack = [];
    dirty = false;
    selectedRows = new Set();
    updateUndoRedoButtons();

    $editorTitle.textContent = `${project} / ${file}`;

    try {
      const result = await api(`/datasets/${encodeURIComponent(project)}/${encodeURIComponent(file)}`);
      data = Array.isArray(result.data) ? result.data : [];
      columns = result.columns || [];
      renderTable();
      showView("editor");
    } catch (e) {
      toast("Failed to load dataset: " + e.message, "error");
    }
  }

  function showView(view) {
    $projectsView.classList.toggle("hidden", view !== "projects");
    $editorView.classList.toggle("hidden", view !== "editor");
  }

  $btnBack.addEventListener("click", async () => {
    if (dirty) {
      const ok = await confirmDialog("Unsaved Changes", "You have unsaved changes. Discard them?");
      if (!ok) return;
    }
    showView("projects");
    loadProjects();
  });

  // ---- Render table ----
  function renderTable(filter = "") {
    if (!data.length && !columns.length) {
      $tableContainer.innerHTML = `<p style="padding:1rem;color:var(--text-muted)">Empty dataset. Add a row to start.</p>`;
      $status.textContent = "0 rows";
      return;
    }
    // Infer columns from data if not provided
    if (!columns.length && data.length) {
      const colSet = new Set();
      data.forEach(row => Object.keys(row).forEach(k => colSet.add(k)));
      columns = Array.from(colSet);
    }

    const lf = filter.toLowerCase();
    let html = `<table><thead><tr><th class="col-select"><input type="checkbox" id="select-all" /></th>`;
    for (const col of columns) {
      html += `<th>${escapeHtml(col)}</th>`;
    }
    html += `</tr></thead><tbody>`;

    data.forEach((row, idx) => {
      // Filter
      if (lf) {
        const text = columns.map(c => stringify(row[c])).join(" ").toLowerCase();
        if (!text.includes(lf)) return;
      }
      const sel = selectedRows.has(idx);
      html += `<tr data-idx="${idx}" class="${sel ? 'selected' : ''}">`;
      html += `<td class="cell-select"><input type="checkbox" data-sel="${idx}" ${sel ? 'checked' : ''}/></td>`;
      for (const col of columns) {
        const val = row[col];
        const isArr = Array.isArray(val);
        if (isArr) {
          const preview = val.length ? val.slice(0, 2).join(", ") + (val.length > 2 ? ` … (${val.length})` : '') : '(empty)';
          html += `<td class="cell-array" data-row="${idx}" data-col="${col}"><span class="arr-preview">${escapeHtml(preview)}</span> <button class="btn btn-small btn-arr-edit" data-arr-row="${idx}" data-arr-col="${col}">✏️</button></td>`;
        } else {
          const display = val == null ? "" : String(val);
          html += `<td contenteditable="true" data-row="${idx}" data-col="${col}">${escapeHtml(display)}</td>`;
        }
      }
      html += `</tr>`;
    });
    html += `</tbody></table>`;
    $tableContainer.innerHTML = html;
    $status.textContent = `${data.length} rows · ${columns.length} columns${dirty ? ' · unsaved changes' : ''}`;

    // wire events
    $tableContainer.querySelectorAll("td[contenteditable]").forEach(td => {
      td.addEventListener("blur", onCellBlur);
    });
    $tableContainer.querySelectorAll(".btn-arr-edit").forEach(btn => {
      btn.addEventListener("click", () => {
        const ri = parseInt(btn.dataset.arrRow);
        const col = btn.dataset.arrCol;
        openArrayEditor(ri, col);
      });
    });
    const selectAll = document.getElementById("select-all");
    if (selectAll) {
      selectAll.addEventListener("change", (e) => {
        if (e.target.checked) {
          data.forEach((_, i) => selectedRows.add(i));
        } else {
          selectedRows.clear();
        }
        renderTable($search.value);
      });
    }
    $tableContainer.querySelectorAll("input[data-sel]").forEach(cb => {
      cb.addEventListener("change", (e) => {
        const i = parseInt(e.target.dataset.sel);
        if (e.target.checked) selectedRows.add(i); else selectedRows.delete(i);
        e.target.closest("tr").classList.toggle("selected", e.target.checked);
        $btnDelRows.disabled = selectedRows.size === 0;
      });
    });
    $btnDelRows.disabled = selectedRows.size === 0;
  }

  // ---- Cell edit ----
  function onCellBlur(e) {
    const td = e.target;
    const rowIdx = parseInt(td.dataset.row);
    const col = td.dataset.col;
    const oldVal = data[rowIdx][col];
    let newVal = td.textContent;

    // Try to parse as JSON for arrays/objects
    try {
      const parsed = JSON.parse(newVal);
      if (typeof parsed === "object") newVal = parsed;
    } catch { /* leave as string */ }

    if (JSON.stringify(oldVal) === JSON.stringify(newVal)) return;

    pushUndo();
    data[rowIdx][col] = newVal;
    markDirty();
  }

  // ---- Add row ----
  $btnAddRow.addEventListener("click", () => {
    pushUndo();
    const newRow = {};
    columns.forEach(c => newRow[c] = "");
    data.push(newRow);
    markDirty();
    renderTable($search.value);
    // Scroll to bottom
    $tableContainer.scrollTop = $tableContainer.scrollHeight;
  });

  // ---- Delete selected rows ----
  $btnDelRows.addEventListener("click", async () => {
    if (selectedRows.size === 0) return;
    const ok = await confirmDialog("Delete Rows", `Delete ${selectedRows.size} selected row(s)?`);
    if (!ok) return;
    pushUndo();
    const indices = Array.from(selectedRows).sort((a, b) => b - a);
    indices.forEach(i => data.splice(i, 1));
    selectedRows.clear();
    markDirty();
    renderTable($search.value);
  });

  // ---- Search ----
  $search.addEventListener("input", () => renderTable($search.value));

  // ================================================
  // ARRAY EDITOR POPUP
  // ================================================
  const $dlgArray = document.getElementById("dialog-array-editor");
  const $arrList  = document.getElementById("array-items-list");
  const $arrTitle = document.getElementById("array-editor-title");
  let _arrRow = null;
  let _arrCol = null;
  let _arrItems = [];

  function openArrayEditor(rowIdx, col) {
    _arrRow = rowIdx;
    _arrCol = col;
    _arrItems = Array.isArray(data[rowIdx][col]) ? [...data[rowIdx][col]] : [];
    $arrTitle.textContent = `Edit "${col}" (row ${rowIdx + 1})`;
    renderArrayItems();
    $dlgArray.showModal();
  }

  function renderArrayItems() {
    $arrList.innerHTML = "";
    _arrItems.forEach((item, i) => {
      const li = document.createElement("li");
      li.className = "arr-item";
      li.innerHTML = `<input type="text" class="arr-input" data-ai="${i}" value="${escapeHtml(String(item))}" /><button class="btn btn-small btn-danger arr-remove" data-ai="${i}" title="Remove">✕</button>`;
      $arrList.appendChild(li);
    });
    // wire
    $arrList.querySelectorAll(".arr-input").forEach(inp => {
      inp.addEventListener("input", (e) => { _arrItems[parseInt(e.target.dataset.ai)] = e.target.value; });
    });
    $arrList.querySelectorAll(".arr-remove").forEach(btn => {
      btn.addEventListener("click", () => { _arrItems.splice(parseInt(btn.dataset.ai), 1); renderArrayItems(); });
    });
  }

  document.getElementById("arr-add-item").addEventListener("click", () => {
    _arrItems.push("");
    renderArrayItems();
    const inputs = $arrList.querySelectorAll(".arr-input");
    if (inputs.length) inputs[inputs.length - 1].focus();
  });

  document.getElementById("arr-save").addEventListener("click", () => {
    pushUndo();
    data[_arrRow][_arrCol] = [..._arrItems];
    markDirty();
    renderTable($search.value);
    $dlgArray.close();
  });

  document.getElementById("arr-cancel").addEventListener("click", () => {
    $dlgArray.close();
  });

  // ================================================
  // UNDO / REDO
  // ================================================
  function pushUndo() {
    undoStack.push(JSON.stringify(data));
    if (undoStack.length > 50) undoStack.shift();
    redoStack = [];
    updateUndoRedoButtons();
  }

  function undo() {
    if (!undoStack.length) return;
    redoStack.push(JSON.stringify(data));
    data = JSON.parse(undoStack.pop());
    markDirty();
    renderTable($search.value);
  }

  function redo() {
    if (!redoStack.length) return;
    undoStack.push(JSON.stringify(data));
    data = JSON.parse(redoStack.pop());
    markDirty();
    renderTable($search.value);
  }

  function updateUndoRedoButtons() {
    $btnUndo.disabled = undoStack.length === 0;
    $btnRedo.disabled = redoStack.length === 0;
  }

  $btnUndo.addEventListener("click", undo);
  $btnRedo.addEventListener("click", redo);

  // ---- Keyboard shortcuts ----
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "z") { e.preventDefault(); undo(); }
    if (e.ctrlKey && e.key === "y") { e.preventDefault(); redo(); }
    if (e.ctrlKey && e.key === "s") { e.preventDefault(); save(); }
  });

  // ================================================
  // SAVE
  // ================================================
  function markDirty() {
    dirty = true;
    $btnSave.disabled = false;
    updateUndoRedoButtons();
    $status.textContent = `${data.length} rows · ${columns.length} columns · unsaved changes`;
  }

  async function save() {
    if (!dirty) return;
    try {
      await api(`/datasets/${encodeURIComponent(currentProject)}/${encodeURIComponent(currentFile)}`, {
        method: "PUT",
        body: JSON.stringify(data),
      });
      dirty = false;
      $btnSave.disabled = true;
      $status.textContent = `${data.length} rows · ${columns.length} columns · saved`;
      toast("Saved!", "success");
    } catch (err) {
      toast("Save failed: " + err.message, "error");
    }
  }

  $btnSave.addEventListener("click", save);

  // ================================================
  // Utility
  // ================================================
  function escapeHtml(s) {
    if (s == null) return "";
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function stringify(v) {
    if (v == null) return "";
    if (typeof v === "object") return JSON.stringify(v);
    return String(v);
  }

  // ================================================
  // Init
  // ================================================
  loadProjects();
})();
