const ICONS = {
  edit: '<svg class="icon icon-sm" viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
  disable: '<svg class="icon icon-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="m5.7 5.7 12.6 12.6"/></svg>',
  adjust: '<svg class="icon icon-sm" viewBox="0 0 24 24"><path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/></svg>',
  phone: '<svg class="icon icon-sm" viewBox="0 0 24 24"><path d="M4 4h4l2 5-2.5 1.5a12 12 0 0 0 6 6L15 14l5 2v4a2 2 0 0 1-2 2C9.5 22 2 14.5 2 6a2 2 0 0 1 2-2Z"/></svg>',
  user: '<svg class="icon icon-sm" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/></svg>',
  contact: '<svg class="icon icon-sm" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 6 8 6 8-6"/></svg>',
  store: '<svg class="icon" viewBox="0 0 24 24"><path d="M4 21V9l8-5 8 5v12"/><path d="M9 21v-6h6v6"/></svg>',
};

// Botón redondo solo con ícono para las acciones de cada registro
function iconButton(action, icon, label) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "icon-action";
  button.dataset.action = action;
  button.title = label;
  button.setAttribute("aria-label", label);
  button.innerHTML = ICONS[icon];
  return button;
}

function initials(name) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

// Buscador de la barra superior: filtra los hijos de cualquier
// contenedor marcado con data-searchable (filas o tarjetas).
function applySearch() {
  const input = document.querySelector(".app-search input");
  if (!input) return;
  const term = input.value.trim().toLowerCase();

  document.querySelectorAll("[data-searchable] > *").forEach((item) => {
    if (item.dataset.emptyState !== undefined) return;
    item.hidden = Boolean(term) && !item.textContent.toLowerCase().includes(term);
  });
}

function initSearch() {
  const input = document.querySelector(".app-search input");
  const containers = document.querySelectorAll("[data-searchable]");
  if (!input || containers.length === 0) return;

  input.disabled = false;
  input.addEventListener("input", applySearch);

  // Las páginas vuelven a pintar sus listas al cargar datos;
  // se reaplica el filtro cada vez que cambian.
  const observer = new MutationObserver(applySearch);
  containers.forEach((container) => {
    observer.observe(container, { childList: true });
  });
}

function getColorMode() {
  return localStorage.getItem("colorMode") || "light";
}

function applyColorMode() {
  const mode = getColorMode();
  document.documentElement.setAttribute("data-theme", mode);
  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.innerHTML =
      mode === "dark"
        ? '<svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
        : '<svg class="icon" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8Z"/></svg>';
  });
}

function setColorMode(mode) {
  localStorage.setItem("colorMode", mode);
  applyColorMode();
}

function markActiveNavLink() {
  const path = window.location.pathname;
  document.querySelectorAll(".app-nav a").forEach((link) => {
    const href = link.getAttribute("href");
    if (href && path.startsWith(href)) {
      link.classList.add("active");
    }
  });
}

async function initSidebarUser() {
  const avatar = document.querySelector("#sidebar-avatar");
  const nameEl = document.querySelector("#sidebar-user-name");
  const roleEl = document.querySelector("#sidebar-user-role");
  if (!avatar) return;

  try {
    const response = await fetch("/auth/me", { credentials: "same-origin" });
    if (!response.ok) return;
    const user = await response.json();

    avatar.textContent = user.nombre
      .split(" ")
      .map((part) => part[0])
      .slice(0, 2)
      .join("")
      .toUpperCase();
    nameEl.textContent = user.nombre;
    roleEl.textContent = user.rol;

    document.querySelectorAll(".app-nav a.admin-only").forEach((el) => {
      el.hidden = user.rol !== "ADMIN";
    });
    document.querySelectorAll(".app-nav a.admin-manager").forEach((el) => {
      el.hidden = !["ADMIN", "GERENTE"].includes(user.rol);
    });
  } catch (error) {
    // silencioso: cada pagina ya maneja sus propios errores de sesion
  }
}

function initLogoutButton() {
  const button = document.querySelector("#logout-button");
  if (!button) return;

  button.addEventListener("click", async () => {
    try {
      await fetch("/auth/logout", { method: "POST", credentials: "same-origin" });
      if (typeof showToast === "function") {
        showToast("Sesión cerrada correctamente", "success", 1200);
      }
      setTimeout(() => {
        window.location.href = "/login";
      }, 700);
    } catch (error) {
      window.location.href = "/login";
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  applyColorMode();
  markActiveNavLink();
  initSidebarUser();
  initLogoutButton();
  initSearch();
  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      setColorMode(getColorMode() === "dark" ? "light" : "dark");
    });
  });
});
