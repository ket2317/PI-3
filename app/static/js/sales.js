let currentUser = null;
let branchProducts = [];
let cart = [];

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
  const select = document.querySelector("#sale-branch-id");
  select.innerHTML = "";
  branches.forEach((b) => {
    const option = document.createElement("option");
    option.value = b.id;
    option.textContent = b.nombre;
    select.appendChild(option);
  });
  if (currentUser.rol !== "ADMIN" && currentUser.sucursal_id) {
    select.value = currentUser.sucursal_id;
    select.disabled = true;
  }
  await loadProductsForBranch();
}

async function loadProductsForBranch() {
  const branchId = Number(document.querySelector("#sale-branch-id").value);
  branchProducts = await apiRequest(`/productos/?sucursal_id=${branchId}`);

  const select = document.querySelector("#item-product-id");
  select.innerHTML = "";
  branchProducts.forEach((p) => {
    const option = document.createElement("option");
    option.value = p.id;
    option.textContent = `${p.codigo} — ${p.nombre} ($${p.precio})`;
    select.appendChild(option);
  });
}

async function loadPaymentMethods() {
  const methods = await apiRequest("/metodos-pago/");
  const select = document.querySelector("#payment-method-id");
  select.innerHTML = "";
  methods.forEach((m) => {
    const option = document.createElement("option");
    option.value = m.id;
    option.textContent = m.nombre;
    select.appendChild(option);
  });
}

function renderCart() {
  const body = document.querySelector("#cart-body");
  body.innerHTML = "";

  let subtotal = 0;
  let iva = 0;

  cart.forEach((item, index) => {
    const product = branchProducts.find((p) => p.id === item.producto_id);
    const itemSubtotal = Number(product.precio) * item.cantidad;
    const itemIva = itemSubtotal * Number(product.iva);

    subtotal += itemSubtotal;
    iva += itemIva;

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${product.nombre}</td>
      <td>${item.cantidad}</td>
      <td>$${Number(product.precio).toFixed(2)}</td>
      <td>$${itemSubtotal.toFixed(2)}</td>
      <td><button type="button" data-index="${index}">Quitar</button></td>
    `;
    row.querySelector("button").addEventListener("click", () => {
      cart.splice(index, 1);
      renderCart();
    });
    body.appendChild(row);
  });

  document.querySelector("#cart-subtotal").textContent = `Subtotal: $${subtotal.toFixed(2)}`;
  document.querySelector("#cart-iva").textContent = `IVA: $${iva.toFixed(2)}`;
  document.querySelector("#cart-total").textContent = `Total: $${(subtotal + iva).toFixed(2)}`;
}

document.querySelector("#sale-branch-id").addEventListener("change", async () => {
  cart = [];
  renderCart();
  try {
    await loadProductsForBranch();
  } catch (error) {
    showError(error.message);
  }
});

document.querySelector("#add-item-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const producto_id = Number(document.querySelector("#item-product-id").value);
  const cantidad = Number(document.querySelector("#item-quantity").value);

  if (!producto_id || cantidad <= 0) {
    return;
  }

  const existing = cart.find((item) => item.producto_id === producto_id);
  if (existing) {
    existing.cantidad += cantidad;
  } else {
    cart.push({ producto_id, cantidad });
  }
  renderCart();
});

document.querySelector("#confirm-sale").addEventListener("click", async () => {
  if (cart.length === 0) {
    showError("Agrega al menos un producto al carrito");
    return;
  }

  try {
    clearError();
    const venta = await apiRequest("/ventas/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sucursal_id: Number(document.querySelector("#sale-branch-id").value),
        metodo_pago_id: Number(document.querySelector("#payment-method-id").value),
        items: cart,
      }),
    });

    showSuccess("Venta registrada correctamente");

    const receipt = document.querySelector("#receipt");
    receipt.hidden = false;
    document.querySelector("#receipt-content").textContent = JSON.stringify(venta, null, 2);

    cart = [];
    renderCart();
    await loadProductsForBranch();
  } catch (error) {
    showError(error.message);
  }
});

(async () => {
  try {
    await loadCurrentUser();
    await loadBranches();
    await loadPaymentMethods();
    renderCart();
  } catch (error) {
    showError(error.message);
  }
})();
