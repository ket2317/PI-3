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
    "dashboard.subtitle": "Resumen general de tu sesión",
    "dashboard.session_title": "Sesión actual",
    "dashboard.my_branch_title": "Mi sucursal",
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
    "inventory.low_stock": "Ver bajo inventario",
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
    "dashboard.subtitle": "Overview of your session",
    "dashboard.session_title": "Current session",
    "dashboard.my_branch_title": "My branch",
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
    "inventory.low_stock": "View low stock",
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

function applyTranslations() {
  const lang = getLanguage();
  document.documentElement.lang = lang;

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.getAttribute("data-i18n");
    const text = translations[lang][key];
    if (text) {
      element.textContent = text;
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