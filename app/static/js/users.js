let currentUser = null;
let roles = [
  { id: 1, nombre: "ADMIN" },
  { id: 2, nombre: "GERENTE" },
  { id: 3, nombre: "CAJERO" },
];
let branches = [];

function showError(message) {
  const el = document.querySelector("#page-error");
  el.textContent = message;
  el.hidden = false;
}
function clearError() {
  document.querySelector("#page-error").hidden = true;
}
function showSuccess(message) {
  const el = document.querySelector("#page-success");
  el.textContent = message;
  el.hidden = false;
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
  document.querySelector("#user-submit").textContent = "Guardar usuario";
  document.querySelector("#user-cancel").hidden = true;
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
  const body = document.querySelector("#users-body");
  body.innerHTML = "";

  users.forEach((user) => {
    const branch = branches.find((b) => b.id === user.sucursal_id);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${user.nombre}</td>
      <td>${user.correo}</td>
      <td>${roleName(user.rol_id)}</td>
      <td>${branch ? branch.nombre : "—"}</td>
      <td>${user.activo ? "Sí" : "No"}</td>
      <td>
        <button type="button" data-action="edit">Editar</button>
        <button type="button" data-action="delete">Desactivar</button>
      </td>
    `;
    row.querySelector('[data-action="edit"]').addEventListener("click", () => editUser(user));
    row.querySelector('[data-action="delete"]').addEventListener("click", () => deactivateUser(user));
    body.appendChild(row);
  });
}

function editUser(user) {
  document.querySelector("#user-id").value = user.id;
  document.querySelector("#user-name").value = user.nombre;
  document.querySelector("#user-email").value = user.correo;
  document.querySelector("#user-role-id").value = user.rol_id;
  document.querySelector("#user-branch-id").value = user.sucursal_id || "";
  document.querySelector("#user-submit").textContent = "Guardar cambios";
  document.querySelector("#user-cancel").hidden = false;
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
    resetForm();
    await loadUsers();
  } catch (error) {
    showError(error.message);
  }
});

document.querySelector("#user-cancel").addEventListener("click", resetForm);

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
