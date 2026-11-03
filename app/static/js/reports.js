let statsRange = { desde: "", hasta: "" };

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

function money(value) {
  return `$${Number(value).toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}

function rangeQuery() {
  const params = new URLSearchParams();
  if (statsRange.desde) params.set("desde", statsRange.desde);
  if (statsRange.hasta) params.set("hasta", statsRange.hasta);
  const query = params.toString();
  return query ? `?${query}` : "";
}

async function loadSummaryIfAdmin(user) {
  if (user.rol !== "ADMIN") return;
  try {
    const summary = await apiRequest("/reportes/resumen");
    document.querySelector("#summary-section").hidden = false;
    document.querySelector("#summary-branches").textContent = summary.sucursales_activas;
    document.querySelector("#summary-products").textContent = summary.productos_activos;
    document.querySelector("#summary-sales").textContent = summary.ventas_totales;
    document.querySelector("#summary-total").textContent = money(summary.monto_total_vendido);
  } catch (error) {
    showError(error.message);
  }
}

// ---------- Estadísticas ----------

async function loadStatistics() {
  const stats = await apiRequest(`/reportes/estadisticas${rangeQuery()}`);

  document.querySelector("#stats-total").textContent = money(stats.total_vendido);
  document.querySelector("#stats-count").textContent = stats.numero_ventas.toLocaleString("es-MX");
  document.querySelector("#stats-average").textContent = money(stats.ticket_promedio);

  renderTopProducts(stats.productos_mas_vendidos);
  renderBranchSales(stats.ventas_por_sucursal);
  renderDailyChart(stats.ventas_por_dia);
}

function renderTopProducts(products) {
  const body = document.querySelector("#top-products-body");
  if (products.length === 0) {
    body.innerHTML = `<tr><td colspan="4" class="empty-state">Sin ventas en este periodo</td></tr>`;
    return;
  }
  body.innerHTML = products
    .map(
      (p) => `
      <tr>
        <td>${escapeHtml(p.nombre)}</td>
        <td>${escapeHtml(p.codigo)}</td>
        <td class="num">${p.cantidad_vendida.toLocaleString("es-MX")}</td>
        <td class="num">${money(p.importe)}</td>
      </tr>`
    )
    .join("");
}

function renderBranchSales(rows) {
  const body = document.querySelector("#branch-sales-body");
  if (rows.length === 0) {
    body.innerHTML = `<tr><td colspan="3" class="empty-state">Sin ventas en este periodo</td></tr>`;
    return;
  }
  body.innerHTML = rows
    .map(
      (r) => `
      <tr>
        <td>${escapeHtml(r.sucursal)}</td>
        <td class="num">${r.numero_ventas.toLocaleString("es-MX")}</td>
        <td class="num">${money(r.total)}</td>
      </tr>`
    )
    .join("");
}

function formatDay(isoDate, options) {
  // La fecha llega como AAAA-MM-DD; se arma en hora local para no recorrer el día
  const [year, month, day] = isoDate.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("es-MX", options);
}

// "Bonito" máximo del eje: 1, 2, 2.5 o 5 por potencia de 10
function niceMax(value) {
  if (value <= 0) return 1;
  const power = 10 ** Math.floor(Math.log10(value));
  const step = [1, 2, 2.5, 5, 10].find((s) => s * power >= value);
  return step * power;
}

function renderDailyChart(days) {
  const container = document.querySelector("#daily-chart");

  if (days.length === 0) {
    container.innerHTML = `<p class="chart-empty">Sin ventas en este periodo</p>`;
    return;
  }

  const width = 720;
  const height = 260;
  const pad = { top: 16, right: 12, bottom: 34, left: 64 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const max = niceMax(Math.max(...days.map((d) => d.total)));
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => t * max);
  const slot = plotW / days.length;
  const barW = Math.max(2, Math.min(28, slot - 2));
  const y = (value) => pad.top + plotH - (value / max) * plotH;

  // Con muchos días solo se rotulan algunos para que no se encimen
  const labelEvery = Math.ceil(days.length / 8);

  const grid = ticks
    .map(
      (t) => `
      <line class="chart-grid" x1="${pad.left}" x2="${width - pad.right}" y1="${y(t)}" y2="${y(t)}"/>
      <text class="chart-axis" x="${pad.left - 8}" y="${y(t) + 4}" text-anchor="end">${money(t).replace(".00", "")}</text>`
    )
    .join("");

  const bars = days
    .map((d, i) => {
      const x = pad.left + i * slot + (slot - barW) / 2;
      const top = y(d.total);
      const h = Math.max(1, pad.top + plotH - top);
      const r = Math.min(4, barW / 2, h);
      // Barra con las esquinas superiores redondeadas y la base recta
      const path = `M${x},${top + h} V${top + r} Q${x},${top} ${x + r},${top} H${x + barW - r} Q${x + barW},${top} ${x + barW},${top + r} V${top + h} Z`;
      const label =
        i % labelEvery === 0
          ? `<text class="chart-axis" x="${x + barW / 2}" y="${height - 12}" text-anchor="middle">${formatDay(d.fecha, { day: "numeric", month: "short" })}</text>`
          : "";
      return `
        <g class="chart-bar" data-index="${i}">
          <rect class="chart-hit" x="${pad.left + i * slot}" y="${pad.top}" width="${slot}" height="${plotH}"/>
          <path class="chart-mark" d="${path}"/>
          ${label}
        </g>`;
    })
    .join("");

  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" aria-hidden="true">
      ${grid}
      <line class="chart-baseline" x1="${pad.left}" x2="${width - pad.right}" y1="${pad.top + plotH}" y2="${pad.top + plotH}"/>
      ${bars}
    </svg>
    <div class="chart-tooltip" hidden></div>
  `;

  const tooltip = container.querySelector(".chart-tooltip");
  container.querySelectorAll(".chart-bar").forEach((bar) => {
    bar.addEventListener("mouseenter", () => {
      const d = days[Number(bar.dataset.index)];
      tooltip.innerHTML = `
        <strong>${formatDay(d.fecha, { weekday: "short", day: "numeric", month: "long" })}</strong>
        <span>${money(d.total)}</span>
        <span>${d.numero_ventas} ${d.numero_ventas === 1 ? "venta" : "ventas"}</span>`;
      tooltip.hidden = false;
      bar.classList.add("is-hover");
    });
    bar.addEventListener("mousemove", (event) => {
      const box = container.getBoundingClientRect();
      const left = Math.min(event.clientX - box.left + 12, box.width - tooltip.offsetWidth - 4);
      tooltip.style.left = `${Math.max(4, left)}px`;
      tooltip.style.top = `${event.clientY - box.top - tooltip.offsetHeight - 10}px`;
    });
    bar.addEventListener("mouseleave", () => {
      tooltip.hidden = true;
      bar.classList.remove("is-hover");
    });
  });
}

// ---------- Historial ----------

async function loadSalesHistory() {
  const ventas = await apiRequest(withSearch(`/reportes/ventas${rangeQuery()}`));
  const body = document.querySelector("#sales-body");
  document.querySelector("#sales-count").textContent = ventas.length;

  if (ventas.length === 0) {
    body.innerHTML = `<tr><td colspan="8" class="empty-state">${emptyMessage("Sin ventas en este periodo")}</td></tr>`;
    return;
  }

  body.innerHTML = ventas
    .map(
      (venta) => `
      <tr>
        <td>#${venta.id}</td>
        <td>${new Date(venta.created_at).toLocaleString("es-MX")}</td>
        <td>${escapeHtml(venta.sucursal)}</td>
        <td>${escapeHtml(venta.usuario)}</td>
        <td>${escapeHtml(venta.metodo_pago)}</td>
        <td class="num">${money(venta.subtotal)}</td>
        <td class="num">${money(venta.iva)}</td>
        <td class="num">${money(venta.total)}</td>
      </tr>`
    )
    .join("");
}

async function reloadReports() {
  await Promise.all([loadStatistics(), loadSalesHistory()]);
}

document.querySelector("#stats-filter").addEventListener("submit", async (event) => {
  event.preventDefault();
  const desde = document.querySelector("#stats-desde").value;
  const hasta = document.querySelector("#stats-hasta").value;
  if (desde && hasta && desde > hasta) {
    showError("La fecha inicial no puede ser posterior a la final");
    return;
  }
  statsRange = { desde, hasta };
  try {
    await reloadReports();
  } catch (error) {
    showError(error.message);
  }
});

document.querySelector("#stats-clear").addEventListener("click", async () => {
  document.querySelector("#stats-desde").value = "";
  document.querySelector("#stats-hasta").value = "";
  statsRange = { desde: "", hasta: "" };
  try {
    await reloadReports();
  } catch (error) {
    showError(error.message);
  }
});

(async () => {
  try {
    const user = await apiRequest("/auth/me");
    await loadSummaryIfAdmin(user);
    await reloadReports();
    onSearch(loadSalesHistory);
  } catch (error) {
    showError(error.message);
  }
})();
