const TOAST_ICONS = {
  success:
    '<svg class="icon" viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></svg>',
  error:
    '<svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 8v5"/><path d="M12 16h.01"/></svg>',
};

function ensureToastStack() {
  let stack = document.querySelector("#toast-stack");
  if (!stack) {
    stack = document.createElement("div");
    stack.id = "toast-stack";
    document.body.appendChild(stack);
  }
  return stack;
}

function showToast(message, type = "success", duration = 4000) {
  const stack = ensureToastStack();

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    ${TOAST_ICONS[type] || TOAST_ICONS.success}
    <span class="toast-message"></span>
    <button type="button" class="toast-close" aria-label="Cerrar">&times;</button>
  `;
  toast.querySelector(".toast-message").textContent = message;

  const remove = () => {
    toast.classList.add("toast-out");
    setTimeout(() => toast.remove(), 180);
  };

  toast.querySelector(".toast-close").addEventListener("click", remove);
  stack.appendChild(toast);

  if (duration > 0) {
    setTimeout(remove, duration);
  }

  return remove;
}

// El servidor a veces manda el error como lista (validaciones de FastAPI).
// Esto lo convierte en texto para que nunca se vea "[object Object]".
function errorDetail(detail) {
  if (!detail) return "";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => (item && item.msg ? String(item.msg).replace(/^Value error, /, "") : String(item)))
      .join(". ");
  }
  if (typeof detail === "object" && detail.msg) return String(detail.msg);
  return "";
}
