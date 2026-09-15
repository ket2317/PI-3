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

(async () => {
  try {
    const user = await apiRequest("/auth/me");
    renderUser(user);
  } catch (error) {
    showError(error.message);
  }
})();
