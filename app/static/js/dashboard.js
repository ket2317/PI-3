function showError(message) {
  const element = document.querySelector("#dashboard-error");
  element.textContent = message;
  element.hidden = false;
}

function hideElements(selector) {
  document.querySelectorAll(selector).forEach((element) => {
    element.hidden = true;
  });
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (response.status === 401) {
    window.location.href = "/login";
    throw new Error("Debes iniciar sesión");
  }

  if (!response.ok) {
    throw new Error(data.detail || "No fue posible completar la operación");
  }

  return data;
}

function renderUser(user) {
  document.querySelector("#current-user").textContent =
    `Usuario: ${user.nombre}`;

  document.querySelector("#current-role").textContent =
    `Rol: ${user.rol}`;

  const branchElement = document.querySelector("#current-branch");

  if (user.sucursal_id) {
    branchElement.textContent =
      `Sucursal asignada: ${user.sucursal_id}`;
  } else {
    branchElement.textContent =
      "Sucursal asignada: Administración general";
  }

  if (user.rol !== "ADMIN") {
    hideElements(".admin-only");
  }

  if (user.rol !== "ADMIN" && user.rol !== "GERENTE") {
    hideElements(".admin-manager");
  }
}

document.querySelector("#logout-button")
  .addEventListener("click", async () => {
    try {
      await apiRequest("/auth/logout", {
        method: "POST",
      });

      window.location.href = "/login";
    } catch (error) {
      showError(error.message);
    }
  });
  async function loadMyBranch(user) {
    if (user.rol !== "GERENTE" || !user.sucursal_id) {
        return;
    }

    const branch = await apiRequest(`/sucursales/${user.sucursal_id}`);

    document.querySelector("#my-branch-section").hidden = false;

    document.querySelector("#branch-name").textContent =
        `Nombre: ${branch.nombre}`;

    document.querySelector("#branch-address").textContent =
        `Dirección: ${branch.direccion}`;

    document.querySelector("#branch-phone").textContent =
        `Teléfono: ${branch.telefono || "Sin registrar"}`;

    document.querySelector("#branch-contact").textContent =
        `Contacto: ${branch.contacto || "Sin registrar"}`;
}
(async () => {
    try {
        const user = await apiRequest("/auth/me");
        renderUser(user);
        await loadMyBranch(user);
    } catch (error) {
        showError(error.message);
    }
})();