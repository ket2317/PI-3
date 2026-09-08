const form = document.querySelector("#login-form");
const errorMessage = document.querySelector("#login-error");
const button = document.querySelector("#login-button");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorMessage.hidden = true;
  button.disabled = true;

  const payload = {
    email: document.querySelector("#email").value.trim(),
    password: document.querySelector("#password").value,
  };

  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      errorMessage.textContent = data.detail || "No fue posible iniciar sesión";
      errorMessage.hidden = false;
      return;
    }
    window.location.href = "/dashboard";
  } catch (error) {
    errorMessage.textContent = "No se pudo conectar con el servidor";
    errorMessage.hidden = false;
  } finally {
    button.disabled = false;
  }
});
