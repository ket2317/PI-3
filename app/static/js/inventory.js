let currentUser = null;
let branchProducts = [];
let currentInventory = [];
let onlyLowStock = false;

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

function isLowStock(item) {
  return item.existencia <= item.stock_minimo;
}

function renderSummary() {
  const low = currentInventory.filter(isLowStock).length;
  const units = currentInventory.reduce((total, item) => total + item.existencia, 0);
  document.querySelector("#summary-products").textContent = currentInventory.length;
  document.querySelector("#summary-low").textContent = low;
  document.querySelector("#summary-units").textContent = units.toLocaleString("es-MX");
}

function renderInventoryTable() {
  renderSummary();

  const list = document.querySelector("#inventory-body");
  list.innerHTML = "";

  const items = onlyLowStock
    ? currentInventory.filter(isLowStock)
    : currentInventory;

  document.querySelector("#inventory-count").textContent = items.length;

  if (items.length === 0) {
    list.innerHTML = `
      <p class="stock-empty" data-empty-state>
        ${onlyLowStock
          ? "No hay productos con bajo inventario en esta sucursal."
          : "Aún no hay existencias registradas en esta sucursal."}
      </p>
    `;
  }

  items.forEach((item) => {
    const product = branchProducts.find((p) => p.id === item.producto_id);
    const low = isLowStock(item);
    // La barra se llena al 100% cuando hay el doble del stock mínimo
    const target = Math.max(item.stock_minimo * 2, 1);
    const percent = Math.min(100, Math.round((item.existencia / target) * 100));

    const row = document.createElement("div");
    row.className = `stock-row${low ? " is-low" : ""}`;
    row.innerHTML = `
      <div>
        <p class="entity-name">${product ? product.nombre : "Producto " + item.producto_id}</p>
        <p class="entity-sub">Código ${product ? product.codigo : item.producto_id}</p>
      </div>
      <div class="stock-level">
        <div class="stock-bar"><span style="width:${percent}%"></span></div>
        <div class="stock-meta">
          <strong>${item.existencia} piezas</strong>
          <span>mínimo ${item.stock_minimo}</span>
        </div>
      </div>
      <div></div>
    `;

    const adjustButton = iconButton("edit", "adjust", "Ajustar existencia");
    adjustButton.addEventListener("click", () => {
      openInventoryModal(item.producto_id);
    });
    row.lastElementChild.appendChild(adjustButton);
    list.appendChild(row);
  });
}

function openInventoryModal(productId) {
  document.querySelector("#inventory-search").value = "";
  renderProductOptions(branchProducts);
  if (productId) {
    document.querySelector("#inventory-product-select").value = productId;
  }
  fillFieldsFromSelectedProduct();
  openModal("inventory-modal");
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
    closeModal("inventory-modal");
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

document.querySelector("#inventory-new").addEventListener("click", () => {
  openInventoryModal(null);
});

document.querySelector("#low-stock-button").addEventListener("click", (event) => {
  onlyLowStock = !onlyLowStock;
  const button = event.currentTarget;
  button.classList.toggle("is-active", onlyLowStock);
  button.setAttribute("aria-pressed", String(onlyLowStock));
  renderInventoryTable();
});
