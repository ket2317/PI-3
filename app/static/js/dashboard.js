async function loadCurrentUser() {
  const response = await fetch("/auth/me", { credentials: "same-origin" });
  if (response.status === 401) {
    window.location.href = "/login";
    return;
  }
  if (!response.ok) {
    document.querySelector("#current-user").textContent = "No fue posible cargar el usuario";
    return;
  }

  const user = await response.json();
  
  document.querySelector("#user-name").textContent = user.nombre;
  document.querySelector("#user-role").textContent = user.rol;
  document.querySelector("#user-branch").textContent = user.sucursal_id ?? "sin sucursal";

  document.querySelectorAll(".admin-only").forEach((element) => {
    element.hidden = user.rol !== "ADMIN";
  });
  document.querySelectorAll(".admin-manager").forEach((element) => {
    element.hidden = !["ADMIN", "GERENTE"].includes(user.rol);
  });
}

document.querySelector("#logout-button").addEventListener("click", async () => {
  await fetch("/auth/logout", { method: "POST", credentials: "same-origin" });
  window.location.href = "/login";
});

loadCurrentUser();
