let currentUser = null;
let branchProducts = [];
let cart = [];

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

function renderProductGrid(products) {
  const grid = document.querySelector("#product-grid");
  grid.innerHTML = "";

  if (products.length === 0) {
    grid.innerHTML = `<p class="product-grid-empty">Sin resultados</p>`;
    return;
  }

  products.forEach((p) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "product-card";
    card.innerHTML = `
      <span class="product-card-icon">
        <svg class="icon icon-sm" viewBox="0 0 24 24"><path d="M21 8 12 3 3 8l9 5 9-5Z"/><path d="M3 8v8l9 5 9-5V8"/></svg>
      </span>
      <span class="product-card-name">${p.nombre}</span>
      <span class="product-card-code">${p.codigo}</span>
      <span class="product-card-price">$${Number(p.precio).toFixed(2)}</span>
    `;
    card.addEventListener("click", () => addToCart(p.id));
    grid.appendChild(card);
  });
}

async function loadProductsForBranch() {
  const branchId = Number(document.querySelector("#sale-branch-id").value);
  branchProducts = await apiRequest(`/productos/?sucursal_id=${branchId}`);
  document.querySelector("#item-search").value = "";
  renderProductGrid(branchProducts);
}

document.querySelector("#item-search").addEventListener("input", (event) => {
  const term = event.target.value.trim().toLowerCase();
  const filtered = term
    ? branchProducts.filter(
        (p) =>
          p.codigo.toLowerCase().includes(term) ||
          p.nombre.toLowerCase().includes(term),
      )
    : branchProducts;
  renderProductGrid(filtered);
});

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

function addToCart(productId) {
  const existing = cart.find((item) => item.producto_id === productId);
  if (existing) {
    existing.cantidad += 1;
  } else {
    cart.push({ producto_id: productId, cantidad: 1 });
  }
  renderCart();
}

function changeQuantity(productId, delta) {
  const item = cart.find((i) => i.producto_id === productId);
  if (!item) return;
  item.cantidad += delta;
  if (item.cantidad <= 0) {
    cart = cart.filter((i) => i.producto_id !== productId);
  }
  renderCart();
}

function removeFromCart(productId) {
  cart = cart.filter((i) => i.producto_id !== productId);
  renderCart();
}

function renderCart() {
  const container = document.querySelector("#cart-items");
  const emptyMessage = document.querySelector("#cart-empty");
  container.innerHTML = "";

  emptyMessage.hidden = cart.length > 0;

  let subtotal = 0;
  let iva = 0;

  cart.forEach((item) => {
    const product = branchProducts.find((p) => p.id === item.producto_id);
    if (!product) return;

    const itemSubtotal = Number(product.precio) * item.cantidad;
    const itemIva = itemSubtotal * Number(product.iva);

    subtotal += itemSubtotal;
    iva += itemIva;

    const row = document.createElement("div");
    row.className = "cart-item";
    row.innerHTML = `
      <span class="cart-item-name">${product.nombre}</span>
      <button type="button" class="cart-item-remove" aria-label="Quitar">&times;</button>
      <span class="cart-item-qty">
        <button type="button" data-action="decrease">−</button>
        <span>${item.cantidad}</span>
        <button type="button" data-action="increase">+</button>
      </span>
      <span class="cart-item-subtotal">$${itemSubtotal.toFixed(2)}</span>
    `;
    row.querySelector('[data-action="decrease"]').addEventListener("click", () =>
      changeQuantity(item.producto_id, -1),
    );
    row.querySelector('[data-action="increase"]').addEventListener("click", () =>
      changeQuantity(item.producto_id, 1),
    );
    row.querySelector(".cart-item-remove").addEventListener("click", () =>
      removeFromCart(item.producto_id),
    );
    container.appendChild(row);
  });

  document.querySelector("#cart-subtotal").textContent = `$${subtotal.toFixed(2)}`;
  document.querySelector("#cart-iva").textContent = `$${iva.toFixed(2)}`;
  document.querySelector("#cart-total").textContent = `$${(subtotal + iva).toFixed(2)}`;
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

function openReceipt(venta) {
  const modal = document.querySelector("#receipt-modal");
  const content = document.querySelector("#receipt-content");

  const lines = venta.detalles
    .map((d) => {
      const product = branchProducts.find((p) => p.id === d.producto_id);
      const name = product ? product.nombre : `Producto ${d.producto_id}`;
      return `<div class="receipt-line"><span>${d.cantidad} × ${name}</span><span>$${Number(d.subtotal).toFixed(2)}</span></div>`;
    })
    .join("");

  content.innerHTML = `
    <p class="receipt-meta">Venta #${venta.id} — ${new Date(venta.created_at).toLocaleString()}</p>
    ${lines}
    <div class="receipt-line"><span>Subtotal</span><span>$${Number(venta.subtotal).toFixed(2)}</span></div>
    <div class="receipt-line"><span>IVA</span><span>$${Number(venta.iva).toFixed(2)}</span></div>
    <div class="receipt-total"><span>Total</span><span>$${Number(venta.total).toFixed(2)}</span></div>
  `;

  modal.hidden = false;
}

document.querySelector("#receipt-close").addEventListener("click", () => {
  document.querySelector("#receipt-modal").hidden = true;
});

document.querySelector("#confirm-sale").addEventListener("click", async () => {
  if (cart.length === 0) {
    showError("Agrega al menos un producto al ticket");
    return;
  }

  try {
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
    openReceipt(venta);

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
