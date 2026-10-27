const form = document.querySelector("#login-form");
const errorMessage = document.querySelector("#login-error");
const button = document.querySelector("#login-button");

// Manejar el envío del formulario de inicio de sesión
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

  // link por si el usuario olvido su contraseña
  const forgotPasswordLink = document.querySelector('.forgot-password-link a');
  if (forgotPasswordLink) {
    forgotPasswordLink.addEventListener('click', (event) => {
      event.preventDefault(); // Bloquea el comportamiento nativo del HTML
      window.location.href = "/auth/forgot-password";
    });
  }

  // Funcionalidad para mostrar/ocultar contraseña
  const togglePasswordBtn = document.querySelector('.toggle-password');
  const passwordInput = document.getElementById('password');

  if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener('click', () => {
      // Alternar el tipo de input
      const isPassword = passwordInput.getAttribute('type') === 'password';
      passwordInput.setAttribute('type', isPassword ? 'text' : 'password');

      // Cambiar el icono del SVG según el estado
      if (isPassword) {
        // Ojo tachado
        togglePasswordBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/></svg>`;
      } else {
        // Ojo normal
        togglePasswordBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`;
      }
    });
  }

  