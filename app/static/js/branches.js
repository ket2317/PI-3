let currentUser = null;
let managers = [];

function showError(message) {
  const el = document.querySelector("#page-error");
  el.textContent = message;
  el.hidden = false;
}

function clearError() {
  const el = document.querySelector("#page-error");
  el.hidden = true;
  el.textContent = "";
}

function showSuccess(message) {
  const el = document.querySelector("#page-success");
  el.textContent = message;
  el.hidden = false;
}

function clearSuccess() {
  const el = document.querySelector("#page-success");
  el.hidden = true;
  el.textContent = "";
}

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
  document.querySelector("#branch-submit").textContent = "Guardar sucursal";
  document.querySelector("#branch-cancel").hidden = true;
  document.querySelector("#branch-active").hidden = true;
  document.querySelector("#branch-active-label").hidden = true;
  clearError();
}

async function loadCurrentUser() {
  currentUser = await apiRequest("/auth/me");
  if (currentUser.rol !== "ADMIN") {
    document.querySelector("#branch-form").hidden = true;
  }
}

async function loadManagers() {
  if (currentUser.rol !== "ADMIN") {
    return;
  }
  const users = await apiRequest("/usuarios/");
  managers = users.filter((u) => u.rol_id === 2 && u.activo);

  const select = document.querySelector("#branch-manager-id");
  select.innerHTML = `<option value="">Sin asignar</option>`;
  managers.forEach((manager) => {
    const option = document.createElement("option");
    option.value = manager.id;
    option.textContent = manager.nombre;
    select.appendChild(option);
  });
}

function editBranch(branch) {
  document.querySelector("#branch-id").value = branch.id;
  document.querySelector("#branch-name").value = branch.nombre;
  document.querySelector("#branch-address").value = branch.direccion;
  document.querySelector("#branch-phone").value = branch.telefono;
  document.querySelector("#branch-contact").value = branch.contacto || "";
  document.querySelector("#branch-manager-id").value = branch.gerente_id || "";

  const activeField = document.querySelector("#branch-active");
  const activeLabel = document.querySelector("#branch-active-label");
  activeField.hidden = false;
  activeLabel.hidden = false;
  activeField.value = String(branch.activo);

  document.querySelector("#branch-submit").textContent = "Guardar cambios";
  document.querySelector("#branch-cancel").hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
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
  const branches = await apiRequest("/sucursales/");
  const body = document.querySelector("#branches-body");
  body.innerHTML = "";

  branches.forEach((branch) => {
    const manager = managers.find((m) => m.id === branch.gerente_id);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${branch.id}</td>
      <td>${branch.nombre}</td>
      <td>${branch.direccion}</td>
      <td>${branch.telefono}</td>
      <td>${branch.contacto || "—"}</td>
      <td>${manager ? manager.nombre : "Sin asignar"}</td>
      <td>${branch.activo ? "Activa" : "Inactiva"}</td>
      <td></td>
    `;

    if (currentUser.rol === "ADMIN") {
      const actionsCell = row.lastElementChild;

      const editButton = document.createElement("button");
      editButton.type = "button";
      editButton.textContent = "Editar";
      editButton.addEventListener("click", () => editBranch(branch));
      actionsCell.appendChild(editButton);

      const deleteButton = document.createElement("button");
      deleteButton.type = "button";
      deleteButton.textContent = "Desactivar";
      deleteButton.addEventListener("click", () => deactivateBranch(branch));
      actionsCell.appendChild(deleteButton);
    }

    body.appendChild(row);
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
    resetForm();
    await loadBranches();
  } catch (error) {
    showError(error.message);
  }
});

document.querySelector("#branch-cancel").addEventListener("click", resetForm);

(async () => {
  try {
    await loadCurrentUser();
    await loadManagers();
    await loadBranches();
  } catch (error) {
    showError(error.message);
  }
})();
