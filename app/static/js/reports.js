async function apiRequest(url) {
  const response = await fetch(url, { credentials: "same-origin" });
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

function showError(message) {
  showToast(message, "error");
}

async function loadSummaryIfAdmin(user) {
  if (user.rol !== "ADMIN") return;
  try {
    const summary = await apiRequest("/reportes/resumen");
    document.querySelector("#summary-section").hidden = false;
    document.querySelector("#summary-branches").textContent = summary.sucursales_activas;
    document.querySelector("#summary-products").textContent = summary.productos_activos;
    document.querySelector("#summary-sales").textContent = summary.ventas_totales;
    document.querySelector("#summary-total").textContent = `$${summary.monto_total_vendido}`;
  } catch (error) {
    showError(error.message);
  }
}

async function loadSalesHistory() {
  const ventas = await apiRequest("/reportes/ventas");
  const body = document.querySelector("#sales-body");
  body.innerHTML = "";

  ventas.forEach((venta) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${new Date(venta.created_at).toLocaleString()}</td>
      <td>${venta.sucursal_id}</td>
      <td>$${venta.subtotal}</td>
      <td>$${venta.iva}</td>
      <td>$${venta.total}</td>
    `;
    body.appendChild(row);
  });
}

(async () => {
  try {
    const user = await apiRequest("/auth/me");
    await loadSummaryIfAdmin(user);
    await loadSalesHistory();
  } catch (error) {
    showError(error.message);
  }
})();
