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
