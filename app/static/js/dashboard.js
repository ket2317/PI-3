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
    throw new Error("Debes iniciar sesión");
  }

  if (!response.ok) {
    throw new Error(data.detail || "No fue posible completar la operación");
  }

  return data;
}

function renderUser(user) {
  document.querySelector("#current-user").textContent =
    `Usuario: ${user.nombre}`;

  document.querySelector("#current-role").textContent =
    `Rol: ${user.rol}`;

  const branchElement = document.querySelector("#current-branch");

  if (user.sucursal_id) {
    branchElement.textContent =
      `Sucursal asignada: ${user.sucursal_id}`;
  } else {
    branchElement.textContent =
      "Sucursal asignada: Administración general";
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

    document.querySelector("#branch-name").textContent =
        `Nombre: ${branch.nombre}`;

    document.querySelector("#branch-address").textContent =
        `Dirección: ${branch.direccion}`;

    document.querySelector("#branch-phone").textContent =
        `Teléfono: ${branch.telefono || "Sin registrar"}`;

    document.querySelector("#branch-contact").textContent =
        `Contacto: ${branch.contacto || "Sin registrar"}`;
}

/* ==========================================================================
   Dashboard: indicadores, gráficos y listas.
   Usa únicamente endpoints existentes:
     /ventas/, /productos/, /metodos-pago/, /sucursales/, /inventario/bajo-stock
   El backend ya filtra por sucursal según el rol; aquí solo se agrega.
   ========================================================================== */

const DashboardUI = (() => {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const DAY_MS = 86400000;
  const MAX_SERIES = 5;

  const state = {
    user: null,
    branches: [],
    branchMap: new Map(),
    days: 30,
    branchId: "",
    data: null,
    requestId: 0,
    series: [],
  };

  const $ = (selector) => document.querySelector(selector);

  /* ---------- Helpers ---------- */

  function t(key, vars = {}) {
    const lang = typeof getLanguage === "function" ? getLanguage() : "es";
    const dict = (typeof translations !== "undefined" && translations[lang]) || {};
    let text = dict[key] !== undefined ? dict[key] : key;
    Object.entries(vars).forEach(([name, value]) => {
      text = text.replace(`{${name}}`, value);
    });
    return text;
  }

  function locale() {
    return typeof getLanguage === "function" && getLanguage() === "en" ? "en-US" : "es-MX";
  }

  function money(value) {
    const number = Number(value) || 0;
    const digits = Math.abs(number) >= 1e5 ? 0 : 2;
    return "$" + number.toLocaleString(locale(), {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    });
  }

  function integer(value) {
    return (Number(value) || 0).toLocaleString(locale());
  }

  function trimDecimal(value) {
    return String(Math.round(value * 10) / 10);
  }

  function compact(value) {
    const abs = Math.abs(value);
    if (abs >= 1e6) return `${trimDecimal(value / 1e6)}M`;
    if (abs >= 1e3) return `${trimDecimal(value / 1e3)}k`;
    return String(Math.round(value));
  }

  // Máximo "redondo" que permite 4 divisiones enteras en el eje Y.
  function niceMax(value) {
    if (value <= 0) return 4;
    const exponent = Math.floor(Math.log10(value));
    const fraction = value / 10 ** exponent;
    const steps = [1, 2, 4, 8, 10];
    const next = steps.find((step) => fraction <= step) || 10;
    return next * 10 ** exponent;
  }

  function startOfDay(date) {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate());
  }

  function addDays(date, amount) {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate() + amount);
  }

  function svgEl(name, attrs = {}) {
    const element = document.createElementNS(SVG_NS, name);
    Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, value));
    return element;
  }

  function htmlEl(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function emptyMessage(className, text) {
    const box = htmlEl("div", className);
    box.innerHTML =
      '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20V10"/><path d="M12 20V4"/><path d="M20 20v-7"/></svg>';
    box.append(htmlEl("span", "", text));
    return box;
  }

  /* ---------- Métricas ---------- */

  function computeMetrics() {
    const { ventas, productos, pagos, stock } = state.data;
    const days = state.days;
    const today = startOfDay(new Date());
    const start = addDays(today, -(days - 1));
    const prevStart = addDays(start, -days);
    const end = addDays(today, 1);

    const productMap = new Map(productos.map((product) => [product.id, product]));
    const daily = Array.from({ length: days }, (_, index) => ({
      date: addDays(start, index),
      total: 0,
      count: 0,
    }));
    const payTotals = new Map();
    const topMap = new Map();

    let revenue = 0;
    let vat = 0;
    let units = 0;
    let count = 0;
    let todayCount = 0;
    let prevRevenue = 0;

    ventas.forEach((venta) => {
      const when = new Date(venta.created_at);
      const total = Number(venta.total) || 0;

      if (when >= start && when < end) {
        revenue += total;
        vat += Number(venta.iva) || 0;
        count += 1;
        if (when >= today) todayCount += 1;

        const index = Math.min(
          days - 1,
          Math.max(0, Math.round((startOfDay(when) - start) / DAY_MS)),
        );
        daily[index].total += total;
        daily[index].count += 1;

        const pay = payTotals.get(venta.metodo_pago_id) || { value: 0, count: 0 };
        pay.value += total;
        pay.count += 1;
        payTotals.set(venta.metodo_pago_id, pay);

        (venta.detalles || []).forEach((detalle) => {
          const quantity = Number(detalle.cantidad) || 0;
          units += quantity;
          const item = topMap.get(detalle.producto_id) || { id: detalle.producto_id, units: 0, revenue: 0 };
          item.units += quantity;
          item.revenue += Number(detalle.subtotal) || 0;
          topMap.set(detalle.producto_id, item);
        });
      } else if (when >= prevStart && when < start) {
        prevRevenue += total;
      }
    });

    // El color sigue a la entidad (método de pago), no a su posición en el ranking.
    const methodsById = [...pagos].sort((a, b) => a.id - b.id);
    const colorIndex = new Map(methodsById.map((method, index) => [method.id, index]));
    const nameById = new Map(pagos.map((method) => [method.id, method.nombre]));

    const payments = [];
    let otherValue = 0;
    let otherCount = 0;
    payTotals.forEach((pay, id) => {
      const index = colorIndex.has(id) ? colorIndex.get(id) : methodsById.length;
      if (index < MAX_SERIES) {
        payments.push({ name: nameById.get(id) || `#${id}`, value: pay.value, count: pay.count, color: index });
      } else {
        otherValue += pay.value;
        otherCount += pay.count;
      }
    });
    if (otherValue > 0) {
      payments.push({ name: t("dashboard.chart.other"), value: otherValue, count: otherCount, color: MAX_SERIES });
    }
    payments.sort((a, b) => b.value - a.value);

    const top = [...topMap.values()]
      .sort((a, b) => b.units - a.units || b.revenue - a.revenue)
      .slice(0, 5)
      .map((item) => ({ ...item, product: productMap.get(item.id) }));

    const lowStock = stock
      .map((row) => ({ ...row, product: productMap.get(row.producto_id) }))
      .filter((row) => row.product)
      .sort((a, b) => a.existencia - b.existencia || a.product.nombre.localeCompare(b.product.nombre));

    return {
      revenue,
      vat,
      units,
      count,
      todayCount,
      prevRevenue,
      daily,
      payments,
      top,
      lowStock,
      activeProducts: productos.length,
    };
  }

  /* ---------- Indicadores ---------- */

  function setKpi(id, value, sub) {
    $(`#kpi-${id}`).textContent = value;
    $(`#kpi-${id}-sub`).textContent = sub;
  }

  function renderKpis(metrics) {
    const days = state.days;
    const canSeeStock = ["ADMIN", "GERENTE"].includes(state.user.rol);

    setKpi("revenue", money(metrics.revenue), t("dashboard.sub.period", { n: days }));
    setKpi("sales", integer(metrics.count), t("dashboard.sub.transactions"));
    setKpi(
      "ticket",
      metrics.count ? money(metrics.revenue / metrics.count) : "—",
      t("dashboard.sub.per_sale"),
    );
    setKpi("units", integer(metrics.units), t("dashboard.sub.units"));
    setKpi("vat", money(metrics.vat), t("dashboard.sub.vat"));
    setKpi("products", integer(metrics.activeProducts), t("dashboard.sub.catalog"));

    // Crecimiento: ingresos del periodo vs. el periodo inmediato anterior.
    const growth = $("#kpi-growth");
    growth.replaceChildren();
    if (metrics.prevRevenue > 0) {
      const change = ((metrics.revenue - metrics.prevRevenue) / metrics.prevRevenue) * 100;
      const arrow = htmlEl("span", `trend ${change >= 0 ? "trend-up" : "trend-down"}`, change >= 0 ? "▲" : "▼");
      arrow.setAttribute("aria-hidden", "true");
      const sign = change > 0 ? "+" : "";
      growth.append(arrow, `${sign}${change.toLocaleString(locale(), { maximumFractionDigits: 1 })}%`);
      $("#kpi-growth-sub").textContent = t("dashboard.sub.vs_prev", { n: days });
    } else {
      growth.textContent = "—";
      $("#kpi-growth-sub").textContent = t("dashboard.sub.no_prev");
    }

    // Octavo indicador: alertas de stock (admin/gerente) o ventas de hoy (cajero).
    if (canSeeStock) {
      const alerts = metrics.lowStock.length;
      setKpi("alerts", integer(alerts), alerts ? t("dashboard.sub.restock") : t("dashboard.sub.all_good"));
    } else {
      setKpi("alerts", integer(metrics.todayCount), t("dashboard.sub.transactions"));
    }
  }

  /* ---------- Gráfico de ventas por día ---------- */

  function renderSalesTable(series) {
    const table = $("#sales-table");
    table.replaceChildren();
    const caption = htmlEl("caption", "", t("dashboard.chart.sales"));
    const head = htmlEl("tr");
    ["dashboard.chart.table_date", "dashboard.chart.table_total", "dashboard.chart.table_count"].forEach((key) => {
      head.append(htmlEl("th", "", t(key)));
    });
    table.append(caption, head);
    series.forEach((point) => {
      const row = htmlEl("tr");
      row.append(
        htmlEl("td", "", point.date.toLocaleDateString(locale())),
        htmlEl("td", "", money(point.total)),
        htmlEl("td", "", String(point.count)),
      );
      table.append(row);
    });
  }

  function renderSalesChart(metrics) {
    const container = $("#sales-chart");
    const tooltip = $("#sales-tooltip");
    const series = metrics.daily;
    state.series = series;

    tooltip.hidden = true;
    container.replaceChildren();
    $("#sales-chart-meta").textContent = t("dashboard.sub.period", { n: state.days });
    renderSalesTable(series);

    if (!series.some((point) => point.total > 0)) {
      container.append(emptyMessage("chart-empty", t("dashboard.chart.empty")));
      return;
    }

    const width = Math.max(container.clientWidth, 240);
    const height = Math.max(container.clientHeight, 208);
    const margin = { top: 12, right: 12, bottom: 24, left: 48 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    const count = series.length;
    const maxValue = niceMax(Math.max(...series.map((point) => point.total)));

    const x = (index) => margin.left + (count === 1 ? innerWidth / 2 : (index / (count - 1)) * innerWidth);
    const y = (value) => margin.top + innerHeight - (value / maxValue) * innerHeight;

    const svg = svgEl("svg", {
      class: "chart-svg",
      width,
      height,
      viewBox: `0 0 ${width} ${height}`,
      role: "img",
      tabindex: "0",
      "aria-label": `${t("dashboard.chart.sales")}: ${t("dashboard.sub.period", { n: state.days })}`,
    });

    // Cuadrícula tenue y etiquetas del eje Y
    for (let step = 0; step <= 4; step += 1) {
      const value = (maxValue * step) / 4;
      const yy = y(value);
      svg.append(svgEl("line", { class: "grid", x1: margin.left, x2: width - margin.right, y1: yy, y2: yy }));
      const label = svgEl("text", { class: "axis-label", x: margin.left - 8, y: yy + 4, "text-anchor": "end" });
      label.textContent = `$${compact(value)}`;
      svg.append(label);
    }

    // Etiquetas del eje X: pocas y repartidas
    const tickTotal = Math.min(count, width < 420 ? 3 : 5);
    const tickIndexes = new Set();
    for (let k = 0; k < tickTotal; k += 1) {
      tickIndexes.add(tickTotal === 1 ? 0 : Math.round((k * (count - 1)) / (tickTotal - 1)));
    }
    const lastTick = Math.max(...tickIndexes);
    tickIndexes.forEach((index) => {
      const anchor = index === 0 ? "start" : index === lastTick && count > 1 ? "end" : "middle";
      const label = svgEl("text", { class: "axis-label", x: x(index), y: height - 6, "text-anchor": anchor });
      label.textContent = series[index].date.toLocaleDateString(locale(), { day: "numeric", month: "short" });
      svg.append(label);
    });

    // Área y línea
    const linePath = series.map((point, index) => `${index ? "L" : "M"}${x(index)},${y(point.total)}`).join(" ");
    svg.append(
      svgEl("path", { class: "area", d: `${linePath} L${x(count - 1)},${y(0)} L${x(0)},${y(0)} Z` }),
      svgEl("path", { class: "line", d: linePath }),
    );

    if (count <= 14) {
      series.forEach((point, index) => {
        svg.append(svgEl("circle", { class: "marker", cx: x(index), cy: y(point.total), r: 4 }));
      });
    }

    // Capa interactiva: línea guía + punto + tooltip
    const crosshair = svgEl("line", { class: "crosshair", y1: margin.top, y2: margin.top + innerHeight, visibility: "hidden" });
    const focusDot = svgEl("circle", { class: "focus-dot", r: 5, visibility: "hidden" });
    const overlay = svgEl("rect", {
      class: "overlay",
      x: margin.left,
      y: margin.top,
      width: innerWidth,
      height: innerHeight,
    });
    svg.append(crosshair, focusDot, overlay);

    let activeIndex = null;

    function showPoint(index) {
      activeIndex = index;
      const point = series[index];
      const cx = x(index);
      const cy = y(point.total);

      crosshair.setAttribute("x1", cx);
      crosshair.setAttribute("x2", cx);
      crosshair.setAttribute("visibility", "visible");
      focusDot.setAttribute("cx", cx);
      focusDot.setAttribute("cy", cy);
      focusDot.setAttribute("visibility", "visible");

      tooltip.replaceChildren(
        htmlEl("span", "tip-date", point.date.toLocaleDateString(locale(), { weekday: "short", day: "numeric", month: "short" })),
        htmlEl("strong", "tip-value", money(point.total)),
        htmlEl(
          "span",
          "tip-meta",
          t(point.count === 1 ? "dashboard.tip.sale_one" : "dashboard.tip.sale_other", { n: point.count }),
        ),
      );
      tooltip.hidden = false;

      const panelOffset = container.offsetTop;
      const tipWidth = tooltip.offsetWidth;
      const tipHeight = tooltip.offsetHeight;
      let left = cx - tipWidth / 2;
      left = Math.max(0, Math.min(left, width - tipWidth));
      let top = cy - tipHeight - 12;
      if (top < 0) top = cy + 12;
      tooltip.style.left = `${left + container.offsetLeft}px`;
      tooltip.style.top = `${top + panelOffset}px`;
    }

    function hidePoint() {
      activeIndex = null;
      crosshair.setAttribute("visibility", "hidden");
      focusDot.setAttribute("visibility", "hidden");
      tooltip.hidden = true;
    }

    function indexFromEvent(event) {
      const rect = svg.getBoundingClientRect();
      const px = event.clientX - rect.left - margin.left;
      return Math.min(count - 1, Math.max(0, Math.round((px / innerWidth) * (count - 1))));
    }

    overlay.addEventListener("pointermove", (event) => showPoint(indexFromEvent(event)));
    overlay.addEventListener("pointerleave", hidePoint);
    svg.addEventListener("focus", () => showPoint(activeIndex === null ? count - 1 : activeIndex));
    svg.addEventListener("blur", hidePoint);
    svg.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      const current = activeIndex === null ? count - 1 : activeIndex;
      const next = event.key === "ArrowLeft" ? Math.max(0, current - 1) : Math.min(count - 1, current + 1);
      showPoint(next);
    });

    container.append(svg);
  }

  /* ---------- Dona de métodos de pago ---------- */

  function renderPayments(metrics) {
    const wrap = $("#payments-chart");
    const legend = $("#payments-legend");
    wrap.replaceChildren();
    legend.replaceChildren();

    const items = metrics.payments;
    const total = items.reduce((sum, item) => sum + item.value, 0);

    if (!items.length || total <= 0) {
      wrap.append(emptyMessage("chart-empty", t("dashboard.chart.empty")));
      return;
    }

    const size = 148;
    const center = size / 2;
    const strokeWidth = 18;
    const radius = center - strokeWidth / 2 - 4;
    const circumference = 2 * Math.PI * radius;
    const gap = items.length > 1 ? 2 : 0;

    const svg = svgEl("svg", {
      class: "donut-svg",
      width: size,
      height: size,
      viewBox: `0 0 ${size} ${size}`,
      role: "img",
      "aria-label": t("dashboard.chart.payments"),
    });

    const main = svgEl("text", { class: "donut-main", x: center, y: center + 2, "text-anchor": "middle" });
    const sub = svgEl("text", { class: "donut-sub", x: center, y: center + 18, "text-anchor": "middle" });
    const resetCenter = () => {
      main.textContent = `$${compact(total)}`;
      sub.textContent = t("dashboard.chart.total");
      svg.classList.remove("is-hovering");
      svg.querySelectorAll(".segment").forEach((segment) => segment.classList.remove("is-active"));
    };

    let offset = 0;
    items.forEach((item) => {
      const fraction = item.value / total;
      const length = Math.max(fraction * circumference - gap, 0.5);
      const seriesVar = item.color >= MAX_SERIES ? "var(--series-other)" : `var(--series-${item.color + 1})`;
      const segment = svgEl("circle", {
        class: "segment",
        cx: center,
        cy: center,
        r: radius,
        fill: "none",
        stroke: seriesVar,
        "stroke-width": strokeWidth,
        "stroke-dasharray": `${length} ${circumference - length}`,
        "stroke-dashoffset": -offset,
        transform: `rotate(-90 ${center} ${center})`,
        tabindex: "0",
        role: "img",
        "aria-label": `${item.name}: ${money(item.value)} (${Math.round(fraction * 100)}%)`,
      });
      const activate = () => {
        svg.classList.add("is-hovering");
        svg.querySelectorAll(".segment").forEach((other) => other.classList.remove("is-active"));
        segment.classList.add("is-active");
        main.textContent = `${Math.round(fraction * 100)}%`;
        sub.textContent = item.name;
      };
      segment.addEventListener("pointerenter", activate);
      segment.addEventListener("focus", activate);
      segment.addEventListener("pointerleave", resetCenter);
      segment.addEventListener("blur", resetCenter);
      svg.append(segment);
      offset += fraction * circumference;

      // Leyenda: el color identifica, el texto lleva el valor.
      const row = htmlEl("li");
      const swatch = htmlEl("span", "legend-swatch");
      swatch.style.background = seriesVar;
      row.append(
        swatch,
        htmlEl("span", "legend-name", item.name),
        htmlEl("span", "legend-value", money(item.value)),
        htmlEl("span", "legend-pct", `${(fraction * 100).toLocaleString(locale(), { maximumFractionDigits: 1 })}% · ${t(item.count === 1 ? "dashboard.tip.sale_one" : "dashboard.tip.sale_other", { n: item.count })}`),
      );
      legend.append(row);
    });

    svg.append(main, sub);
    resetCenter();
    wrap.append(svg);
  }

  /* ---------- Productos destacados ---------- */

  function branchLabel(product) {
    const showBranch = state.user.rol === "ADMIN" && !state.branchId && state.branches.length > 1;
    if (!showBranch || !product) return "";
    const branch = state.branchMap.get(product.sucursal_id);
    return branch ? ` · ${branch.nombre}` : "";
  }

  function renderTopProducts(metrics) {
    const list = $("#top-products-list");
    list.replaceChildren();

    if (!metrics.top.length) {
      const empty = htmlEl("li");
      empty.dataset.emptyState = "";
      empty.append(emptyMessage("list-empty", t("dashboard.top.empty")));
      list.append(empty);
      return;
    }

    const maxUnits = Math.max(...metrics.top.map((item) => item.units), 1);
    metrics.top.forEach((item, index) => {
      const name = item.product ? item.product.nombre : `#${item.id}`;
      const row = htmlEl("li", "rank-item");
      const bar = htmlEl("div", "rank-bar");
      const fill = htmlEl("span");
      fill.style.width = `${Math.max(4, (item.units / maxUnits) * 100)}%`;
      bar.append(fill);

      const top = htmlEl("div", "rank-top");
      top.append(htmlEl("strong", "rank-name", name), htmlEl("span", "rank-value", money(item.revenue)));

      const main = htmlEl("div", "rank-main");
      main.append(
        top,
        bar,
        htmlEl("span", "rank-sub", `${t("dashboard.top.units", { n: integer(item.units) })}${branchLabel(item.product)}`),
      );

      row.append(htmlEl("span", "rank-pos", String(index + 1)), main);
      list.append(row);
    });
  }

  /* ---------- Inventario bajo ---------- */

  function renderLowStock(metrics) {
    const list = $("#low-stock-list");
    list.replaceChildren();

    if (!metrics.lowStock.length) {
      const empty = htmlEl("li");
      empty.dataset.emptyState = "";
      empty.innerHTML =
        '<div class="list-empty"><svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg><span></span></div>';
      empty.querySelector("span").textContent = t("dashboard.stock.empty");
      list.append(empty);
      return;
    }

    const visible = metrics.lowStock.slice(0, 5);
    visible.forEach((row) => {
      const out = row.existencia <= 0;
      const item = htmlEl("li", "stock-item");
      const main = htmlEl("div", "stock-main");
      main.append(
        htmlEl("strong", "stock-name", row.product.nombre),
        htmlEl(
          "span",
          "stock-sub",
          `${t("dashboard.stock.detail", { a: integer(row.existencia), b: integer(row.stock_minimo) })}${branchLabel(row.product)}`,
        ),
      );
      item.append(main, htmlEl("span", `badge${out ? " badge-out" : ""}`, t(out ? "dashboard.stock.out" : "dashboard.stock.low")));
      list.append(item);
    });

    const remaining = metrics.lowStock.length - visible.length;
    if (remaining > 0) {
      const more = htmlEl("li", "stock-more", t("dashboard.stock.more", { n: remaining }));
      more.dataset.emptyState = "";
      list.append(more);
    }
  }

  /* ---------- Render / carga ---------- */

  function render() {
    if (!state.data) return;
    const metrics = computeMetrics();
    renderKpis(metrics);
    renderSalesChart(metrics);
    renderPayments(metrics);
    renderTopProducts(metrics);
    renderLowStock(metrics);
    $("#dashboard").classList.remove("is-loading");
  }

  async function load() {
    const dash = $("#dashboard");
    const requestId = ++state.requestId;
    dash.classList.add("is-refetching");

    const rol = state.user.rol;
    const query = rol === "ADMIN" && state.branchId ? `?sucursal_id=${encodeURIComponent(state.branchId)}` : "";
    const canSeeStock = rol === "ADMIN" || rol === "GERENTE";

    const results = await Promise.allSettled([
      apiRequest(`/ventas/${query}`),
      apiRequest(`/productos/${query}`),
      apiRequest("/metodos-pago/"),
      canSeeStock ? apiRequest(`/inventario/bajo-stock${query}`) : Promise.resolve([]),
    ]);

    // Si el usuario cambió de sucursal mientras cargaba, se descarta esta respuesta.
    if (requestId !== state.requestId) return;

    const pick = (index) => {
      const result = results[index];
      return result.status === "fulfilled" && Array.isArray(result.value) ? result.value : [];
    };

    const failed = results.find((result) => result.status === "rejected");
    if (failed) showError(failed.reason.message);

    state.data = {
      ventas: pick(0),
      productos: pick(1),
      pagos: pick(2),
      stock: pick(3),
    };

    render();
    dash.classList.remove("is-refetching");
  }

  /* ---------- Configuración por rol y filtros ---------- */

  function setupRole(user) {
    const canSeeStock = user.rol === "ADMIN" || user.rol === "GERENTE";

    if (!canSeeStock) {
      $("#low-stock-panel").hidden = true;
      $("#kpi-alerts-label").setAttribute("data-i18n", "dashboard.kpi.today");
      document.querySelector('[data-role-icon="stock"]').hidden = true;
      document.querySelector('[data-role-icon="today"]').hidden = false;
      $("#kpi-alerts-card").classList.remove("tone-red");
      $("#kpi-alerts-card").classList.add("tone-gold");
      if (typeof applyTranslations === "function") applyTranslations();
    }
  }

  async function loadBranches(user) {
    try {
      const branches = await apiRequest("/sucursales/");
      state.branches = Array.isArray(branches) ? branches : [];
      state.branchMap = new Map(state.branches.map((branch) => [branch.id, branch]));
    } catch (error) {
      state.branches = [];
      return;
    }

    if (user.sucursal_id && state.branchMap.has(user.sucursal_id)) {
      $("#current-branch").textContent =
        `Sucursal asignada: ${state.branchMap.get(user.sucursal_id).nombre}`;
    }

    if (user.rol === "ADMIN" && state.branches.length) {
      const select = $("#branch-filter");
      state.branches.forEach((branch) => {
        const option = document.createElement("option");
        option.value = String(branch.id);
        option.textContent = branch.nombre;
        select.append(option);
      });
      $("#branch-filter-wrap").hidden = false;
    }
  }

  function bindFilters() {
    const period = $("#period-filter");
    period.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-days]");
      if (!button) return;
      state.days = Number(button.dataset.days);
      period.querySelectorAll("button").forEach((other) => {
        other.setAttribute("aria-pressed", String(other === button));
      });
      render();
    });

    $("#branch-filter").addEventListener("change", (event) => {
      state.branchId = event.target.value;
      load();
    });

    // Los textos dinámicos se vuelven a pintar al cambiar de idioma
    // (i18n.js actualiza el idioma en su propio manejador del clic).
    document.querySelectorAll("[data-lang-toggle]").forEach((button) => {
      button.addEventListener("click", () => setTimeout(render, 0));
    });

    // Redibuja el gráfico de líneas cuando cambia el ancho disponible.
    const chart = $("#sales-chart");
    if (typeof ResizeObserver === "function") {
      let lastWidth = chart.clientWidth;
      let lastHeight = chart.clientHeight;
      let frame = null;
      new ResizeObserver(() => {
        const sameSize =
          Math.abs(chart.clientWidth - lastWidth) < 2 && Math.abs(chart.clientHeight - lastHeight) < 2;
        if (sameSize || !state.data) return;
        lastWidth = chart.clientWidth;
        lastHeight = chart.clientHeight;
        cancelAnimationFrame(frame);
        frame = requestAnimationFrame(() => renderSalesChart(computeMetrics()));
      }).observe(chart);
    }
  }

  async function init(user) {
    state.user = user;
    setupRole(user);
    bindFilters();
    await loadBranches(user);
    await load();
  }

  return { init };
})();

(async () => {
    try {
        const user = await apiRequest("/auth/me");
        renderUser(user);
        loadMyBranch(user).catch((error) => showError(error.message));
        await DashboardUI.init(user);
    } catch (error) {
        showError(error.message);
    }
})();