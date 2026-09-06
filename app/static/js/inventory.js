let currentUser = null;

async function apiRequest(url, options = {}) {
  const response = await fetch(url, { credentials: "same-origin", ...options });
  const data = await response.json().catch(() => ({}));
  if (response.status === 401) { window.location.href = "/login"; throw new Error("Debes iniciar sesión"); }
  if (response.status === 403) throw new Error("No tienes permiso para esta operación");
  if (response.status === 404) throw new Error("Recurso no encontrado");
  if (response.status === 422) throw new Error("Revisa los campos enviados");
  if (!response.ok) throw new Error(data.detail || `Error ${response.status}`);
  return data;
}

function showError(message) {
  const element = document.querySelector("#page-error");
  element.textContent = message;
  element.hidden = false;
}

function renderInventory(inventory) {
  const body = document.querySelector("#inventory-body");
  body.innerHTML = "";
  inventory.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${item.producto_id}</td><td>${item.existencia}</td><td>${item.stock_minimo}</td>`;
    body.appendChild(row);
  });
}

async function loadInventory() {
  try {
    const branchInput = document.querySelector("#inventory-branch-id");
    let url = "/inventario/";
    if (currentUser.rol === "ADMIN" && branchInput.value) {
      url += `?sucursal_id=${Number(branchInput.value)}`;
    }
    const inventory = await apiRequest(url);
    renderInventory(inventory);
  } catch (error) {
    showError(error.message);
  }
}

document.querySelector("#inventory-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const branchValue = document.querySelector("#inventory-branch-id").value;
  const productId = document.querySelector("#inventory-product-id").value;

  const payload = {
    existencia: Number(document.querySelector("#inventory-quantity").value),
    stock_minimo: Number(document.querySelector("#inventory-minimum").value),
    sucursal_id: currentUser.rol === "ADMIN" && branchValue ? Number(branchValue) : null,
  };

  try {
    await apiRequest(`/inventario/${productId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    await loadInventory();
  } catch (error) {
    showError(error.message);
  }
});

(async () => {
  try {
    currentUser = await apiRequest("/auth/me");
    await loadInventory();
  } catch (error) {
    showError(error.message);
  }
})();