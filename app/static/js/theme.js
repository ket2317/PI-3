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

// Buscador de la barra superior. Cada página registra con onSearch()
// la función que vuelve a pedir su lista a la API con ?q=.
const SEARCH_DELAY_MS = 300;
let searchHandler = null;

function getSearchTerm() {
  const input = document.querySelector(".app-search input");
  return input ? input.value.trim() : "";
}

// Agrega ?q= (o &q=) a una URL de la API si hay texto en el buscador
function withSearch(url) {
  const term = getSearchTerm();
  if (!term) return url;
  return `${url}${url.includes("?") ? "&" : "?"}q=${encodeURIComponent(term)}`;
}

function onSearch(handler) {
  searchHandler = handler;
  const input = document.querySelector(".app-search input");
  if (input) input.disabled = false;
}

function emptyMessage(defaultText) {
  return getSearchTerm() ? "Sin resultados" : defaultText;
}

function initSearch() {
  const input = document.querySelector(".app-search input");
  if (!input) return;

  let timer = null;
  let running = false;
  let lastSearched = null;

  // Las búsquedas se hacen una a la vez; si el texto cambió mientras se
  // esperaba la respuesta, se repite al final para que la lista coincida
  // con lo último que se escribió.
  async function runSearch() {
    if (!searchHandler || running) return;
    running = true;
    try {
      while (lastSearched !== getSearchTerm()) {
        lastSearched = getSearchTerm();
        await searchHandler(lastSearched);
      }
    } catch (error) {
      if (typeof showToast === "function") showToast(error.message, "error");
    } finally {
      running = false;
    }
  }

  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(runSearch, SEARCH_DELAY_MS);
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

// Aviso de privacidad: se muestra hasta que el usuario lo acepta y no se
// puede cerrar de otra forma (ni con Esc ni haciendo clic afuera).
function showPrivacyNotice() {
  if (document.querySelector(".privacy-dialog")) return;

  const dialog = document.createElement("dialog");
  dialog.className = "confirm-dialog privacy-dialog";
  dialog.innerHTML = `
    <div class="confirm-icon privacy-icon">
      <svg class="icon" viewBox="0 0 24 24"><path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6Z"/><path d="m9 12 2 2 4-4"/></svg>
    </div>
    <h2>Aviso de privacidad</h2>
    <p>
      Antes de usar Vendora debes aceptar el aviso de privacidad y las políticas de uso.
      En él se explica qué datos personales se recaban, para qué se usan y cómo ejercer
      tus derechos ARCO.
    </p>
    <p><a href="/aviso-de-privacidad" target="_blank" rel="noopener">Leer el aviso completo</a></p>
    <div class="confirm-actions">
      <button type="button" class="confirm-ok privacy-accept">Acepto el aviso de privacidad</button>
    </div>
  `;

  // Chrome deja cerrar con Esc aunque se cancele el evento cuando la
  // ventana se abrió sin un clic; si se cierra sin aceptar, se vuelve a abrir.
  let accepted = false;
  dialog.addEventListener("cancel", (event) => event.preventDefault());
  dialog.addEventListener("close", () => {
    if (!accepted) dialog.showModal();
  });

  const accept = dialog.querySelector(".privacy-accept");
  accept.addEventListener("click", async () => {
    accept.disabled = true;
    try {
      const response = await fetch("/privacidad/aceptar", {
        method: "POST",
        credentials: "same-origin",
      });
      if (!response.ok) throw new Error();
      accepted = true;
      dialog.close();
      dialog.remove();
      if (typeof showToast === "function") showToast("Aviso de privacidad aceptado", "success");
    } catch (error) {
      accept.disabled = false;
      if (typeof showToast === "function") showToast("No se pudo registrar la aceptación", "error");
    }
  });

  document.body.appendChild(dialog);
  dialog.showModal();
}

// Muestra solo las secciones que el rol puede usar. Mientras no se conoce
// el rol, el CSS oculta las secciones restringidas.
function applyNavRole(rol) {
  const shell = document.querySelector(".app-shell");
  if (shell) shell.dataset.rol = rol;
  document.querySelectorAll(".app-nav a.admin-only").forEach((el) => {
    el.hidden = rol !== "ADMIN";
  });
  document.querySelectorAll(".app-nav a.admin-manager").forEach((el) => {
    el.hidden = !["ADMIN", "GERENTE"].includes(rol);
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

    if (user.acepto_privacidad === false) {
      showPrivacyNotice();
    }

    applyNavRole(user.rol);
    try {
      sessionStorage.setItem("vendora-rol", user.rol);
    } catch (error) {}
  } catch (error) {
    // silencioso: cada pagina ya maneja sus propios errores de sesion
  }
}

const SESSION_STORAGE_KEYS = ["token", "access_token", "user"];

function confirmLogout() {
  return new Promise((resolve) => {
    const dialog = document.createElement("dialog");
    dialog.className = "confirm-dialog";
    dialog.innerHTML = `
      <div class="confirm-icon">
        <svg class="icon" viewBox="0 0 24 24"><path d="M10.3 3.9 2 18a2 2 0 0 0 1.7 3h16.6a2 2 0 0 0 1.7-3L14.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
      </div>
      <h2>¿Cerrar sesión?</h2>
      <p>Tendrás que volver a iniciar sesión para seguir usando el sistema.</p>
      <div class="confirm-actions">
        <button type="button" class="confirm-cancel">Cancelar</button>
        <button type="button" class="confirm-ok">Cerrar sesión</button>
      </div>
    `;

    const close = (result) => {
      dialog.close();
      dialog.remove();
      resolve(result);
    };
    dialog.querySelector(".confirm-cancel").addEventListener("click", () => close(false));
    dialog.querySelector(".confirm-ok").addEventListener("click", () => close(true));
    dialog.addEventListener("cancel", (event) => {
      event.preventDefault();
      close(false);
    });

    document.body.appendChild(dialog);
    dialog.showModal();
    dialog.querySelector(".confirm-cancel").focus();
  });
}

function initLogoutButton() {
  const button = document.querySelector("#logout-button");
  if (!button) return;

  button.addEventListener("click", async (event) => {
    event.preventDefault();
    if (!(await confirmLogout())) return;
    // Datos de sesión guardados en el navegador; se conservan tema, idioma y menú
    SESSION_STORAGE_KEYS.forEach((key) => localStorage.removeItem(key));
    try {
      sessionStorage.removeItem("vendora-rol");
    } catch (error) {}
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


function initSidebarToggle() {
  const sidebar = document.querySelector("#app-sidebar");
  const toggle = document.querySelector("#sidebar-toggle");
  const shell = document.querySelector(".app-shell");

  if (!sidebar || !toggle || !shell) return;

  const storageKey = "vendora-sidebar-collapsed";

  function updateSidebar(collapsed) {
    shell.classList.toggle("sidebar-collapsed", collapsed);

    toggle.setAttribute("aria-expanded", String(!collapsed));
    toggle.setAttribute(
      "aria-label",
      collapsed ? "Expandir menú" : "Contraer menú"
    );
    toggle.title = collapsed ? "Expandir menú" : "Contraer menú";
  }

  // Recuperar el estado guardado al cambiar de página
  const savedState = localStorage.getItem(storageKey);
  updateSidebar(savedState === "true");

  // El estado inicial se aplica sin animación; las transiciones vuelven
  // a activarse después del primer cuadro
  requestAnimationFrame(() => {
    requestAnimationFrame(() => shell.classList.remove("no-sidebar-transition"));
  });

  // Expandir o contraer al presionar la flecha
  toggle.addEventListener("click", () => {
    const collapsed = !shell.classList.contains("sidebar-collapsed");

    updateSidebar(collapsed);
    localStorage.setItem(storageKey, String(collapsed));
  });
}



document.addEventListener("DOMContentLoaded", () => {
  applyColorMode();
  markActiveNavLink();
  initSidebarUser();
  initLogoutButton();
  initSearch();
  initSidebarToggle();
  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      setColorMode(getColorMode() === "dark" ? "light" : "dark");
    });
  });
});
