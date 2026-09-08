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
  if (response.status === 403) {
    throw new Error("No tienes permiso para esta operación");
  }
  if (response.status === 404) {
    throw new Error("Recurso no encontrado");
  }
  if (response.status === 422) {
    throw new Error("Revisa los campos enviados");
  }
  if (!response.ok) {
    throw new Error(data.detail || `Error ${response.status}`);
  }
  return data;
}

function showError(message) {
  const element = document.querySelector("#page-error");
  element.textContent = message;
  element.hidden = false;
}

function clearError() {
  const element = document.querySelector("#page-error");
  element.hidden = true;
  element.textContent = "";
}

async function loadBranches() {
  try {
    clearError();
    const branches = await apiRequest("/sucursales/");
    const body = document.querySelector("#branches-body");
    body.innerHTML = "";

    branches.forEach((branch) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${branch.id}</td>
        <td>${branch.nombre}</td>
        <td>${branch.direccion}</td>
        <td>${branch.telefono}</td>
        <td>${branch.contacto || ""}</td>
        <td>${branch.gerente_id || "Sin asignar"}</td>
      `;
      body.appendChild(row);
    });
  } catch (error) {
    showError(error.message);
  }
}

document.querySelector("#branch-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();
  const managerId = document.querySelector("#branch-manager-id").value;

  const payload = {
    nombre: document.querySelector("#branch-name").value.trim(),
    direccion: document.querySelector("#branch-address").value.trim(),
    telefono: document.querySelector("#branch-phone").value.trim(),
    contacto: document.querySelector("#branch-contact").value.trim() || null,
    gerente_id: managerId ? Number(managerId) : null,
  };

  try {
    await apiRequest("/sucursales/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    event.target.reset();
    await loadBranches();
  } catch (error) {
    showError(error.message);
  }
});

loadBranches();
