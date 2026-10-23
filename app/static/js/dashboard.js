function showError(message) {
  showToast(message, "error");
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
    throw new Error(translateKey("error.session_expired") || "Debes iniciar sesión");
  }

  if (!response.ok) {
    throw new Error(data.detail || translateKey("error.generic") || "No fue posible completar la operación");
  }

  return data;
}

function renderUser(user) {
  // Traducimos usando las etiquetas correspondientes del diccionario
  const userLabel = translateKey("dashboard.user");
  const roleLabel = translateKey("dashboard.role");
  const assignedBranchLabel = translateKey("dashboard.assigned_branch");
  const generalAdminText = translateKey("dashboard.general_admin");

  document.querySelector("#current-user").textContent =
    `${userLabel}: ${user.nombre || translateKey("branch.no_data")}`;

  // Mapeamos el rol del usuario a una clave del diccionario si existe, o mostramos el valor original
  const roleKey = `role.${user.rol ? user.rol.toLowerCase() : ''}`;
  const translatedRole = translations[getLanguage()][roleKey] || user.rol || "Sin rol";

  document.querySelector("#current-role").textContent =
    `${roleLabel}: ${translatedRole}`;

  const branchElement = document.querySelector("#current-branch");

  if (user.sucursal_id) {
    branchElement.textContent =
      `${assignedBranchLabel}: ${user.sucursal_id}`;
  } else {
    branchElement.textContent =
      `${assignedBranchLabel}: ${generalAdminText}`;
  }

  if (user.rol !== "ADMIN") {
    hideElements(".admin-only");
  }

  if (user.rol !== "ADMIN" && user.rol !== "GERENTE") {
    hideElements(".admin-manager");
  }
}

async function loadMyBranch(user) {
    if (user.rol !== "GERENTE" || !user.sucursal_id) {
        return;
    }

    const branch = await apiRequest(`/sucursales/${user.sucursal_id}`);

    document.querySelector("#my-branch-section").hidden = false;

    // Usamos translateKey para obtener las etiquetas traducidas en tiempo real
    document.querySelector("#branch-name").textContent =
        `${translateKey("branch.name")}: ${branch.nombre}`;

    document.querySelector("#branch-address").textContent =
        `${translateKey("branch.address")}: ${branch.direccion}`;

    document.querySelector("#branch-phone").textContent =
        `${translateKey("branch.phone")}: ${branch.telefono || translateKey("branch.no_data")}`;

    document.querySelector("#branch-contact").textContent =
        `${translateKey("branch.contact")}: ${branch.contacto || translateKey("branch.no_data")}`;
}

// Hacemos la función de carga accesible globalmente por si cambian de idioma
window.reloadDashboardData = async function() {
    try {
        const user = await apiRequest("/auth/me");
        renderUser(user);
        await loadMyBranch(user);
    } catch (error) {
        showError(error.message);
    }
};

(async () => {
    await window.reloadDashboardData();
})();