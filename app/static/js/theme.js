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
  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      setColorMode(getColorMode() === "dark" ? "light" : "dark");
    });
  });
});
