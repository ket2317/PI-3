let currentUser = null;
let managers = [];
let branches = [];

function showError(message) {
  showToast(message, "error");
}

function clearError() {}

function showSuccess(message) {
  showToast(message, "success");
}

function clearSuccess() {}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, { credentials: "same-origin", ...options });
  const data = await response.json().catch(() => ({}));

  if (response.status === 401) {
    window.location.href = "/login";
    throw new Error("Debes iniciar sesión");
  }
  if (!response.ok) {
    throw new Error(data.detail || `Error ${response.status}`);
  }
  return data;
}

function resetForm() {
  document.querySelector("#branch-form").reset();
  document.querySelector("#branch-id").value = "";
  document.querySelector("#branch-modal-title").textContent = "Añadir sucursal";
  document.querySelector("#branch-submit").textContent = "Guardar sucursal";
  document.querySelector("#branch-active").hidden = true;
  document.querySelector("#branch-active-label").hidden = true;
  renderManagerOptions(null);
  clearError();
}

async function loadCurrentUser() {
  currentUser = await apiRequest("/auth/me");
  document.querySelector("#branch-new").hidden = currentUser.rol !== "ADMIN";
}

async function loadManagers() {
  if (currentUser.rol !== "ADMIN") {
    return;
  }
  const users = await apiRequest("/usuarios/");
  managers = users.filter((u) => u.rol_id === 2 && u.activo);
}

function renderManagerOptions(editingBranchId) {
  const select = document.querySelector("#branch-manager-id");
  const previousValue = select.value;

  const takenByOtherBranch = new Set(
    branches
      .filter((b) => b.gerente_id && b.id !== editingBranchId)
      .map((b) => b.gerente_id),
  );

  select.innerHTML = `<option value="">Sin asignar</option>`;
  managers
    .filter((manager) => !takenByOtherBranch.has(manager.id))
    .forEach((manager) => {
      const option = document.createElement("option");
      option.value = manager.id;
      option.textContent = manager.nombre;
      select.appendChild(option);
    });

  select.value = previousValue;
}

function editBranch(branch) {
  document.querySelector("#branch-id").value = branch.id;
  document.querySelector("#branch-name").value = branch.nombre;
  document.querySelector("#branch-address").value = branch.direccion;
  document.querySelector("#branch-phone").value = branch.telefono;
  document.querySelector("#branch-contact").value = branch.contacto || "";
  renderManagerOptions(branch.id);
  document.querySelector("#branch-manager-id").value = branch.gerente_id || "";

  const activeField = document.querySelector("#branch-active");
  const activeLabel = document.querySelector("#branch-active-label");
  activeField.hidden = false;
  activeLabel.hidden = false;
  activeField.value = String(branch.activo);

  document.querySelector("#branch-modal-title").textContent = "Editar sucursal";
  document.querySelector("#branch-submit").textContent = "Guardar cambios";
  openModal("branch-modal");
}

async function deactivateBranch(branch) {
  if (!window.confirm(`¿Desactivar la sucursal "${branch.nombre}"?`)) {
    return;
  }
  try {
    clearError();
    clearSuccess();
    await apiRequest(`/sucursales/${branch.id}`, { method: "DELETE" });
    showSuccess("Sucursal desactivada correctamente");
    await loadBranches();
  } catch (error) {
    showError(error.message);
  }
}

async function loadBranches() {
  branches = await apiRequest("/sucursales/");
  renderManagerOptions(document.querySelector("#branch-id").value ? Number(document.querySelector("#branch-id").value) : null);

  const grid = document.querySelector("#branches-grid");
  grid.innerHTML = "";
  document.querySelector("#branches-count").textContent = branches.length;

  if (branches.length === 0) {
    grid.innerHTML = `<p class="empty-card" data-empty-state>Aún no hay sucursales registradas.</p>`;
  }

  branches.forEach((branch) => {
    const manager = managers.find((m) => m.id === branch.gerente_id);
    const card = document.createElement("article");
    card.className = `entity-card${branch.activo ? "" : " is-inactive"}`;
    card.innerHTML = `
      <div class="entity-head">
        <div class="entity-avatar is-square">${ICONS.store}</div>
        <div>
          <p class="entity-name">${branch.nombre}</p>
          <p class="entity-sub">${branch.direccion}</p>
        </div>
      </div>
      <div class="entity-facts">
        <span>${ICONS.phone} ${branch.telefono || "Sin teléfono"}</span>
        <span>${ICONS.user} ${manager ? manager.nombre : "Sin gerente asignado"}</span>
        ${branch.contacto ? `<span>${ICONS.contact} ${branch.contacto}</span>` : ""}
      </div>
      <div class="entity-foot">
        <span class="badge ${branch.activo ? "badge-success" : "badge-muted"}">${branch.activo ? "Activa" : "Inactiva"}</span>
        <div class="entity-actions"></div>
      </div>
    `;

    if (currentUser.rol === "ADMIN") {
      const actions = card.querySelector(".entity-actions");

      const editButton = iconButton("edit", "edit", "Editar");
      editButton.addEventListener("click", () => editBranch(branch));
      actions.appendChild(editButton);

      if (branch.activo) {
        const deleteButton = iconButton("delete", "disable", "Desactivar");
        deleteButton.addEventListener("click", () => deactivateBranch(branch));
        actions.appendChild(deleteButton);
      }
    }

    grid.appendChild(card);
  });
}

document.querySelector("#branch-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const branchId = document.querySelector("#branch-id").value;
  const managerValue = document.querySelector("#branch-manager-id").value;

  const payload = {
    nombre: document.querySelector("#branch-name").value.trim(),
    direccion: document.querySelector("#branch-address").value.trim(),
    telefono: document.querySelector("#branch-phone").value.trim(),
    contacto: document.querySelector("#branch-contact").value.trim() || null,
    gerente_id: managerValue ? Number(managerValue) : null,
  };

  if (branchId) {
    payload.activo = document.querySelector("#branch-active").value === "true";
  }

  try {
    clearError();
    clearSuccess();

    const url = branchId ? `/sucursales/${branchId}` : "/sucursales/";
    await apiRequest(url, {
      method: branchId ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    showSuccess(branchId ? "Sucursal actualizada correctamente" : "Sucursal creada correctamente");
    closeModal("branch-modal");
    await loadBranches();
  } catch (error) {
    showError(error.message);
  }
});

document.querySelector("#branch-new").addEventListener("click", () => {
  resetForm();
  openModal("branch-modal");
});

document.querySelector("#branch-modal").addEventListener("close", resetForm);

(async () => {
  try {
    await loadCurrentUser();
    await loadManagers();
    await loadBranches();
  } catch (error) {
    showError(error.message);
  }
})();
