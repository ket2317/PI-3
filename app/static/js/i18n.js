const translations = {
  es: {
    "sidebar.subtitle": "Panel de control",
    "nav.dashboard": "Dashboard",
    "nav.branches": "Sucursales",
    "nav.products": "Productos",
    "nav.inventory": "Inventario",
    "nav.sales": "Ventas",
    "nav.users": "Usuarios",
    "nav.reports": "Reportes",
    "nav.logout": "Cerrar sesión",
    "topbar.search": "Buscar...",
    "dashboard.title": "Panel principal",
    "dashboard.subtitle": "Resumen de ventas e inventario",
    "dashboard.session_title": "Sesión actual",
    "dashboard.my_branch_title": "Mi sucursal",
    "dashboard.filter.period": "Periodo",
    "dashboard.filter.branch": "Sucursal",
    "dashboard.filter.all_branches": "Todas las sucursales",
    "dashboard.period.7": "7 días",
    "dashboard.period.30": "30 días",
    "dashboard.period.90": "90 días",
    "dashboard.kpi.revenue": "Ingresos",
    "dashboard.kpi.sales": "Ventas",
    "dashboard.kpi.ticket": "Ticket promedio",
    "dashboard.kpi.units": "Productos vendidos",
    "dashboard.kpi.vat": "IVA",
    "dashboard.kpi.growth": "Crecimiento",
    "dashboard.kpi.products": "Productos activos",
    "dashboard.kpi.alerts": "Alertas de stock",
    "dashboard.kpi.today": "Ventas de hoy",
    "dashboard.sub.period": "Últimos {n} días",
    "dashboard.sub.transactions": "Transacciones",
    "dashboard.sub.per_sale": "Por venta",
    "dashboard.sub.units": "Unidades",
    "dashboard.sub.vat": "Incluido en ingresos",
    "dashboard.sub.vs_prev": "vs. {n} días previos",
    "dashboard.sub.no_prev": "Sin periodo previo",
    "dashboard.sub.catalog": "En catálogo",
    "dashboard.sub.restock": "Por reponer",
    "dashboard.sub.all_good": "Todo en orden",
    "dashboard.chart.sales": "Ventas por día",
    "dashboard.chart.payments": "Métodos de pago",
    "dashboard.chart.total": "Total",
    "dashboard.chart.other": "Otros",
    "dashboard.chart.empty": "Sin ventas en este periodo",
    "dashboard.chart.table_date": "Fecha",
    "dashboard.chart.table_total": "Ingresos",
    "dashboard.chart.table_count": "Ventas",
    "dashboard.tip.sale_one": "{n} venta",
    "dashboard.tip.sale_other": "{n} ventas",
    "dashboard.top.title": "Productos destacados",
    "dashboard.top.meta": "Por unidades vendidas",
    "dashboard.top.units": "{n} uds.",
    "dashboard.top.empty": "Aún no hay ventas en este periodo",
    "dashboard.stock.title": "Inventario bajo",
    "dashboard.stock.view": "Ver inventario",
    "dashboard.stock.out": "Agotado",
    "dashboard.stock.low": "Stock bajo",
    "dashboard.stock.detail": "Existencia {a} · mínimo {b}",
    "dashboard.stock.empty": "Todos los productos tienen existencia suficiente",
    "dashboard.stock.more": "y {n} más",
    "dashboard.stock.count": "{n} por reponer",
    "products.title": "Productos",
    "products.subtitle": "Catálogo de productos por sucursal",
    "products.back": "Volver al panel",
    "products.add_title": "Añadir producto",
    "sales.title": "Punto de venta",
    "sales.subtitle": "Cobra productos y genera el comprobante",
    "sales.confirm": "Confirmar venta",
    "sales.search_title": "Productos",
    "sales.cart_title": "Ticket actual",
    "inventory.title": "Inventario",
    "inventory.subtitle": "Existencias por sucursal",
    "inventory.low_stock": "Bajo inventario",
    "inventory.form_title": "Actualizar existencia",
    "users.title": "Usuarios",
    "users.subtitle": "Gerentes y cajeros del sistema",
    "users.add_title": "Añadir usuario",
    "reports.title": "Reportes",
    "reports.subtitle": "Historial de ventas y resumen general",
    "branches.title": "Sucursales",
    "branches.subtitle": "Sedes de la empresa",
    "branches.add_title": "Añadir sucursal",
  },
  en: {
    "sidebar.subtitle": "Control panel",
    "nav.dashboard": "Dashboard",
    "nav.branches": "Branches",
    "nav.products": "Products",
    "nav.inventory": "Inventory",
    "nav.sales": "Sales",
    "nav.users": "Users",
    "nav.reports": "Reports",
    "nav.logout": "Log out",
    "topbar.search": "Search...",
    "dashboard.title": "Dashboard",
    "dashboard.subtitle": "Sales and inventory overview",
    "dashboard.session_title": "Current session",
    "dashboard.my_branch_title": "My branch",
    "dashboard.filter.period": "Period",
    "dashboard.filter.branch": "Branch",
    "dashboard.filter.all_branches": "All branches",
    "dashboard.period.7": "7 days",
    "dashboard.period.30": "30 days",
    "dashboard.period.90": "90 days",
    "dashboard.kpi.revenue": "Revenue",
    "dashboard.kpi.sales": "Sales",
    "dashboard.kpi.ticket": "Average ticket",
    "dashboard.kpi.units": "Units sold",
    "dashboard.kpi.vat": "VAT",
    "dashboard.kpi.growth": "Growth",
    "dashboard.kpi.products": "Active products",
    "dashboard.kpi.alerts": "Stock alerts",
    "dashboard.kpi.today": "Sales today",
    "dashboard.sub.period": "Last {n} days",
    "dashboard.sub.transactions": "Transactions",
    "dashboard.sub.per_sale": "Per sale",
    "dashboard.sub.units": "Units",
    "dashboard.sub.vat": "Included in revenue",
    "dashboard.sub.vs_prev": "vs. previous {n} days",
    "dashboard.sub.no_prev": "No previous period",
    "dashboard.sub.catalog": "In catalog",
    "dashboard.sub.restock": "To restock",
    "dashboard.sub.all_good": "All good",
    "dashboard.chart.sales": "Daily sales",
    "dashboard.chart.payments": "Payment methods",
    "dashboard.chart.total": "Total",
    "dashboard.chart.other": "Other",
    "dashboard.chart.empty": "No sales in this period",
    "dashboard.chart.table_date": "Date",
    "dashboard.chart.table_total": "Revenue",
    "dashboard.chart.table_count": "Sales",
    "dashboard.tip.sale_one": "{n} sale",
    "dashboard.tip.sale_other": "{n} sales",
    "dashboard.top.title": "Top products",
    "dashboard.top.meta": "By units sold",
    "dashboard.top.units": "{n} units",
    "dashboard.top.empty": "No sales in this period yet",
    "dashboard.stock.title": "Low stock",
    "dashboard.stock.view": "View inventory",
    "dashboard.stock.out": "Out of stock",
    "dashboard.stock.low": "Low stock",
    "dashboard.stock.detail": "In stock {a} · minimum {b}",
    "dashboard.stock.empty": "All products are sufficiently stocked",
    "dashboard.stock.more": "and {n} more",
    "dashboard.stock.count": "{n} to restock",
    "products.title": "Products",
    "products.subtitle": "Product catalog by branch",
    "products.back": "Back to dashboard",
    "products.add_title": "Add product",
    "sales.title": "Point of sale",
    "sales.subtitle": "Charge products and generate the receipt",
    "sales.confirm": "Confirm sale",
    "sales.search_title": "Products",
    "sales.cart_title": "Current ticket",
    "inventory.title": "Inventory",
    "inventory.subtitle": "Stock by branch",
    "inventory.low_stock": "Low stock",
    "inventory.form_title": "Update stock",
    "users.title": "Users",
    "users.subtitle": "Managers and cashiers in the system",
    "users.add_title": "Add user",
    "reports.title": "Reports",
    "reports.subtitle": "Sales history and general summary",
    "branches.title": "Branches",
    "branches.subtitle": "Company locations",
    "branches.add_title": "Add branch",
  },
};

function getLanguage() {
  return localStorage.getItem("lang") || "es";
}

function setLanguage(lang) {
  localStorage.setItem("lang", lang);
  applyTranslations();
}

// Cambia solo el texto del elemento; los íconos SVG que contiene se conservan.
function setTextKeepingIcons(element, text) {
  const textNodes = [...element.childNodes].filter(
    (node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim(),
  );

  if (element.children.length === 0 || textNodes.length === 0) {
    if (element.children.length === 0) {
      element.textContent = text;
    } else {
      element.append(` ${text}`);
    }
    return;
  }

  textNodes[0].textContent = ` ${text} `;
  textNodes.slice(1).forEach((node) => node.remove());
}

function applyTranslations() {
  const lang = getLanguage();
  document.documentElement.lang = lang;

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.getAttribute("data-i18n");
    const text = translations[lang][key];
    if (text) {
      setTextKeepingIcons(element, text);
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    const key = element.getAttribute("data-i18n-placeholder");
    const text = translations[lang][key];
    if (text) {
      element.setAttribute("placeholder", text);
    }
  });

  document.querySelectorAll("[data-lang-toggle]").forEach((button) => {
    button.textContent = lang === "es" ? "EN" : "ES";
  });
}

document.addEventListener("DOMContentLoaded", () => {
  applyTranslations();
  document.querySelectorAll("[data-lang-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      setLanguage(getLanguage() === "es" ? "en" : "es");
    });
  });
});