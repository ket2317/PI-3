// Cualquier enlace al aviso de privacidad lo abre en una ventana modal
// en lugar de salir de la página. El aviso va dentro de un iframe para que
// sus estilos no cambien los de la página que lo abre.
(function () {
  if (window.openPrivacyModal) return;

  const STYLE = `
    .privacy-modal {
      width: min(860px, calc(100vw - 32px));
      height: min(88vh, 900px);
      max-width: none;
      max-height: none;
      margin: auto;
      inset: 0;
      padding: 0;
      border: none;
      border-radius: 16px;
      overflow: hidden;
      background: var(--color-surface, #fff);
      color: var(--color-text, #1f1f1f);
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
    }
    .privacy-modal[open] { display: flex; flex-direction: column; }
    .privacy-modal::backdrop { background: rgba(20, 12, 14, 0.55); }
    .privacy-modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px 18px;
      border-bottom: 1px solid var(--color-border, #e6e1e2);
    }
    .privacy-modal-header h2 {
      margin: 0;
      font-size: 1.05rem;
      font-weight: 700;
    }
    .privacy-modal-close {
      width: 34px;
      height: 34px;
      min-height: 0;
      margin: 0;
      padding: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: none;
      border-radius: 8px;
      background: transparent;
      color: inherit;
      cursor: pointer;
      font-size: 1.4rem;
      line-height: 1;
    }
    .privacy-modal-close:hover { background: rgba(0, 0, 0, 0.06); }
    .privacy-modal iframe {
      flex: 1;
      width: 100%;
      border: none;
      background: #fff;
    }
  `;

  function ensureStyle() {
    if (document.querySelector("#privacy-modal-style")) return;
    const style = document.createElement("style");
    style.id = "privacy-modal-style";
    style.textContent = STYLE;
    document.head.appendChild(style);
  }

  function openPrivacyModal() {
    ensureStyle();
    let dialog = document.querySelector(".privacy-modal");
    if (!dialog) {
      dialog = document.createElement("dialog");
      dialog.className = "privacy-modal";
      dialog.setAttribute("aria-label", "Aviso de privacidad");
      dialog.innerHTML = `
        <div class="privacy-modal-header">
          <h2>Aviso de Privacidad y Políticas de Uso</h2>
          <button type="button" class="privacy-modal-close" aria-label="Cerrar">&times;</button>
        </div>
        <iframe title="Aviso de privacidad" src="/aviso-de-privacidad?embed=1"></iframe>
      `;
      dialog.querySelector(".privacy-modal-close").addEventListener("click", () => dialog.close());
      // Clic fuera del recuadro también la cierra
      dialog.addEventListener("click", (event) => {
        if (event.target === dialog) dialog.close();
      });
      document.body.appendChild(dialog);
    }
    if (!dialog.open) dialog.showModal();
  }

  document.addEventListener("click", (event) => {
    const link = event.target.closest('a[href^="/aviso-de-privacidad"]');
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey) return;
    event.preventDefault();
    openPrivacyModal();
  });

  window.openPrivacyModal = openPrivacyModal;
})();
