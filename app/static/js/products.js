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

function clearError() {
  const element = document.querySelector("#page-error");
  element.hidden = true;
  element.textContent = "";
}

async function loadProducts() {
  try {
    clearError();
    const products = await apiRequest("/productos/");
    const body = document.querySelector("#products-body");
    body.innerHTML = "";
    products.forEach((p) => {
      const row = document.createElement("tr");
      row.innerHTML = `<td>${p.id}</td><td>${p.codigo}</td><td>${p.nombre}</td><td>${p.precio}</td><td>${p.iva}</td>`;
      body.appendChild(row);
    });
  } catch (error) {
    showError(error.message);
  }
}

document.querySelector("#product-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();
  const payload = {
    codigo: document.querySelector("#product-code").value.trim(),
    nombre: document.querySelector("#product-name").value.trim(),
    precio: document.querySelector("#product-price").value,
    iva: document.querySelector("#product-tax").value,
    categoria_id: Number(document.querySelector("#product-category-id").value) || null,
  };

  try {
    await apiRequest("/productos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    event.target.reset();
    await loadProducts();
  } catch (error) {
    showError(error.message);
  }
});

loadProducts();
