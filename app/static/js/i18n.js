const translations = {
  es: {
    "nav.branches": "Sucursales",
    "nav.products": "Productos",
    "nav.inventory": "Inventario",
    "nav.sales": "Ventas",
    "nav.users": "Usuarios",
    "nav.reports": "Reportes",
    "nav.logout": "Cerrar sesión",
    "products.title": "Productos",
    "products.back": "Volver al panel",
    "sales.title": "Punto de venta",
    "sales.confirm": "Confirmar venta",
    "inventory.title": "Inventario",
    "inventory.low_stock": "Ver bajo inventario",
  },
  en: {
    "nav.branches": "Branches",
    "nav.products": "Products",
    "nav.inventory": "Inventory",
    "nav.sales": "Sales",
    "nav.users": "Users",
    "nav.reports": "Reports",
    "nav.logout": "Log out",
    "products.title": "Products",
    "products.back": "Back to dashboard",
    "sales.title": "Point of sale",
    "sales.confirm": "Confirm sale",
    "inventory.title": "Inventory",
    "inventory.low_stock": "View low stock",
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