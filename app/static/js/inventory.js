let currentUser = null;
let branchProducts = [];
let currentInventory = [];

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

async function loadCurrentUser() {
  currentUser = await apiRequest("/auth/me");
}

async function loadBranches() {
  const branches = await apiRequest("/sucursales/");
  const select = document.querySelector("#inventory-branch-id");
  select.innerHTML = "";
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

function fillFieldsFromSelectedProduct() {
  const select = document.querySelector("#inventory-product-select");
  const productId = Number(select.value) || null;
  document.querySelector("#inventory-product-id").value = productId || "";

  const item = currentInventory.find((i) => i.producto_id === productId);
  document.querySelector("#inventory-quantity").value = item ? item.existencia : 0;
  document.querySelector("#inventory-minimum").value = item ? item.stock_minimo : 5;
}

function renderProductOptions(products) {
  const select = document.querySelector("#inventory-product-select");
  const previous = select.value;
  select.innerHTML = "";

  if (products.length === 0) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "Sin resultados";
    select.appendChild(option);
    fillFieldsFromSelectedProduct();
    return;
  }

  products.forEach((p) => {
    const option = document.createElement("option");
    option.value = p.id;
    option.textContent = `${p.codigo} — ${p.nombre}`;
    select.appendChild(option);
  });

  if (products.some((p) => String(p.id) === previous)) {
    select.value = previous;
  }

  fillFieldsFromSelectedProduct();
}

async function loadProductsForBranch() {
  const branchId = Number(document.querySelector("#inventory-branch-id").value);
  branchProducts = await apiRequest(`/productos/?sucursal_id=${branchId}`);
  document.querySelector("#inventory-search").value = "";
  renderProductOptions(branchProducts);
}

async function loadInventory() {
  const branchId = Number(document.querySelector("#inventory-branch-id").value);
  currentInventory = await apiRequest(`/inventario/?sucursal_id=${branchId}`);
  renderInventoryTable();
  fillFieldsFromSelectedProduct();
}

function renderInventoryTable() {
  const body = document.querySelector("#inventory-body");
  body.innerHTML = "";

  currentInventory.forEach((item) => {
    const product = branchProducts.find((p) => p.id === item.producto_id);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${product ? product.codigo : item.producto_id}</td>
      <td>${product ? product.nombre : "—"}</td>
      <td>${item.existencia}</td>
      <td>${item.stock_minimo}</td>
    `;
    body.appendChild(row);
  });
}

document.querySelector("#inventory-search").addEventListener("input", (event) => {
  const term = event.target.value.trim().toLowerCase();
  const filtered = term
    ? branchProducts.filter(
        (p) =>
          p.codigo.toLowerCase().includes(term) ||
          p.nombre.toLowerCase().includes(term),
      )
    : branchProducts;
  renderProductOptions(filtered);
});

document
  .querySelector("#inventory-product-select")
  .addEventListener("change", fillFieldsFromSelectedProduct);

document.querySelector("#inventory-branch-id").addEventListener("change", async () => {
  try {
    clearError();
    await loadProductsForBranch();
    await loadInventory();
  } catch (error) {
    showError(error.message);
  }
});

document.querySelector("#inventory-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const productId = document.querySelector("#inventory-product-id").value;
  if (!productId) {
    showError("Selecciona un producto de la lista");
    return;
  }

  const payload = {
    existencia: Number(document.querySelector("#inventory-quantity").value),
    stock_minimo: Number(document.querySelector("#inventory-minimum").value),
    sucursal_id: Number(document.querySelector("#inventory-branch-id").value),
  };

  try {
    clearError();
    await apiRequest(`/inventario/${productId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    showSuccess("Inventario actualizado correctamente");
    await loadInventory();
  } catch (error) {
    showError(error.message);
  }
});

(async () => {
  try {
    await loadCurrentUser();
    await loadBranches();
    await loadProductsForBranch();
    await loadInventory();
  } catch (error) {
    showError(error.message);
  }
})();

