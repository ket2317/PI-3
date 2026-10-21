let currentUser = null;
let roles = [
  { id: 1, nombre: "ADMIN" },
  { id: 2, nombre: "GERENTE" },
  { id: 3, nombre: "CAJERO" },
];
let branches = [];

function showError(message) {
  showToast(message, "error");
}
function clearError() {}
function showSuccess(message) {
  showToast(message, "success");
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
  document.querySelector("#user-form").reset();
  document.querySelector("#user-id").value = "";
  document.querySelector("#user-modal-title").textContent = "Añadir usuario";
  document.querySelector("#user-submit").textContent = "Guardar usuario";
  document.querySelector("#user-password").required = true;
  document.querySelector("#user-password-hint").hidden = true;
  if (currentUser && currentUser.rol === "GERENTE") {
    document.querySelector("#user-branch-id").value = currentUser.sucursal_id;
  }
  clearError();
}

async function loadCurrentUser() {
  currentUser = await apiRequest("/auth/me");
}

async function loadBranches() {
  branches = await apiRequest("/sucursales/");
  const select = document.querySelector("#user-branch-id");
  select.innerHTML = `<option value="">Sin sucursal (ADMIN)</option>`;
  branches.forEach((b) => {
    const option = document.createElement("option");
    option.value = b.id;
    option.textContent = b.nombre;
    select.appendChild(option);
  });
  if (currentUser.rol === "GERENTE") {
    select.value = currentUser.sucursal_id;
    select.disabled = true;
  }
}

function getRoleOptions() {
  if (currentUser.rol === "GERENTE") {
    return roles.filter((r) => r.nombre === "CAJERO");
  }
  return roles;
}

function renderRoleOptions() {
  const select = document.querySelector("#user-role-id");
  select.innerHTML = "";
  getRoleOptions().forEach((role) => {
    const option = document.createElement("option");
    option.value = role.id;
    option.textContent = role.nombre;
    select.appendChild(option);
  });
}

function roleName(rolId) {
  const role = roles.find((r) => r.id === rolId);
  return role ? role.nombre : rolId;
}

async function loadUsers() {
  const users = await apiRequest("/usuarios/");
  const grid = document.querySelector("#users-grid");
  grid.innerHTML = "";
  document.querySelector("#users-count").textContent = users.length;

  if (users.length === 0) {
    grid.innerHTML = `<p class="empty-card" data-empty-state>Aún no hay usuarios registrados.</p>`;
  }

  users.forEach((user) => {
    const branch = branches.find((b) => b.id === user.sucursal_id);
    const role = roleName(user.rol_id);
    const card = document.createElement("article");
    card.className = `entity-card${user.activo ? "" : " is-inactive"}`;
    card.innerHTML = `
      <div class="entity-head">
        <div class="entity-avatar badge-role-${String(role).toLowerCase()}">${initials(user.nombre)}</div>
        <div>
          <p class="entity-name">${user.nombre}</p>
          <p class="entity-sub">${user.correo}</p>
        </div>
      </div>
      <div class="entity-tags">
        <span class="badge badge-role-${String(role).toLowerCase()}">${role}</span>
        <span class="badge badge-muted">${branch ? branch.nombre : role === "ADMIN" ? "Todas las sucursales" : "Sin sucursal"}</span>
      </div>
      <div class="entity-foot">
        <span class="badge ${user.activo ? "badge-success" : "badge-muted"}">${user.activo ? "Activo" : "Inactivo"}</span>
        <div class="entity-actions"></div>
      </div>
    `;

    const actions = card.querySelector(".entity-actions");
    const editButton = iconButton("edit", "edit", "Editar");
    editButton.addEventListener("click", () => editUser(user));
    actions.appendChild(editButton);

    if (user.activo) {
      const deleteButton = iconButton("delete", "disable", "Desactivar");
      deleteButton.addEventListener("click", () => deactivateUser(user));
      actions.appendChild(deleteButton);
    }

    grid.appendChild(card);
  });
}

function editUser(user) {
  document.querySelector("#user-id").value = user.id;
  document.querySelector("#user-name").value = user.nombre;
  document.querySelector("#user-email").value = user.correo;
  document.querySelector("#user-role-id").value = user.rol_id;
  document.querySelector("#user-branch-id").value = user.sucursal_id || "";
  document.querySelector("#user-modal-title").textContent = "Editar usuario";
  document.querySelector("#user-submit").textContent = "Guardar cambios";
  document.querySelector("#user-password").required = false;
  document.querySelector("#user-password-hint").hidden = false;
  openModal("user-modal");
}

async function deactivateUser(user) {
  if (!window.confirm(`¿Desactivar a "${user.nombre}"?`)) return;
  try {
    clearError();
    await apiRequest(`/usuarios/${user.id}`, { method: "DELETE" });
    showSuccess("Usuario desactivado correctamente");
    await loadUsers();
  } catch (error) {
    showError(error.message);
  }
}

document.querySelector("#user-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const userId = document.querySelector("#user-id").value;
  const branchValue = document.querySelector("#user-branch-id").value;

  const payload = {
    nombre: document.querySelector("#user-name").value.trim(),
    correo: document.querySelector("#user-email").value.trim(),
    rol_id: Number(document.querySelector("#user-role-id").value),
    sucursal_id: branchValue ? Number(branchValue) : null,
  };

  const password = document.querySelector("#user-password").value;

  try {
    clearError();
    let url;
    let method;

    if (userId) {
      url = `/usuarios/${userId}`;
      method = "PUT";
      payload.password = password || null;
      payload.activo = true;
    } else {
      url = "/usuarios/";
      method = "POST";
      payload.password = password;
    }

    await apiRequest(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    showSuccess(userId ? "Usuario actualizado correctamente" : "Usuario creado correctamente");
    closeModal("user-modal");
    await loadUsers();
  } catch (error) {
    showError(error.message);
  }
});

document.querySelector("#user-new").addEventListener("click", () => {
  resetForm();
  openModal("user-modal");
});

document.querySelector("#user-modal").addEventListener("close", resetForm);

(async () => {
  try {
    await loadCurrentUser();
    renderRoleOptions();
    await loadBranches();
    await loadUsers();
  } catch (error) {
    showError(error.message);
  }
})();
