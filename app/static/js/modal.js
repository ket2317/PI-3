// Ventanas modales para los formularios: se abren con un botón y se
// cierran con "Cancelar", la X, la tecla Esc o clic fuera del recuadro.

function openModal(id) {
  const dialog = document.getElementById(id);
  if (dialog && !dialog.open) {
    dialog.showModal();
  }
}

function closeModal(id) {
  const dialog = document.getElementById(id);
  if (dialog && dialog.open) {
    dialog.close();
  }
}

document.querySelectorAll("dialog.modal").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      dialog.close();
    }
  });

  dialog.querySelectorAll("[data-modal-close]").forEach((button) => {
    button.addEventListener("click", () => dialog.close());
  });
});
