// Agrega un botón de ojo a cada campo de contraseña para mostrarla u ocultarla.
// También funciona con los campos que aparecen después (ventanas que se crean al vuelo).
(function () {
  if (window.enhancePasswordInputs) return;

  const EYE =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>';
  const EYE_OFF =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9.9 9.9a3 3 0 1 0 4.2 4.2"/><path d="M10.7 5.1A10.4 10.4 0 0 1 12 5c7 0 10 7 10 7a13.2 13.2 0 0 1-1.7 2.7"/><path d="M6.6 6.6A13.5 13.5 0 0 0 2 12s3 7 10 7a9.7 9.7 0 0 0 5.4-1.6"/><path d="m2 2 20 20"/></svg>';

  const STYLE = `
    .pw-wrap { position: relative; display: block; width: 100%; }
    .pw-wrap > input { width: 100%; padding-right: 44px !important; }
    .pw-toggle {
      position: absolute;
      top: 50%;
      right: 6px;
      transform: translateY(-50%);
      width: 32px;
      height: 32px;
      min-height: 0;
      margin: 0;
      padding: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: none;
      border-radius: 6px;
      background: transparent;
      color: var(--color-text-muted, #777);
      cursor: pointer;
      box-shadow: none;
    }
    .pw-toggle:hover { color: var(--color-primary, #7a3038); background: rgba(0, 0, 0, 0.05); }
    .pw-toggle svg {
      width: 18px;
      height: 18px;
      fill: none;
      stroke: currentColor;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
  `;

  function ensureStyle() {
    if (document.querySelector("#pw-toggle-style")) return;
    const style = document.createElement("style");
    style.id = "pw-toggle-style";
    style.textContent = STYLE;
    document.head.appendChild(style);
  }

  function setVisible(input, button, visible) {
    input.type = visible ? "text" : "password";
    button.innerHTML = visible ? EYE_OFF : EYE;
    button.setAttribute("aria-label", visible ? "Ocultar contraseña" : "Mostrar contraseña");
    button.title = visible ? "Ocultar contraseña" : "Mostrar contraseña";
  }

  function enhance(input) {
    // El login ya trae su propio ojo
    if (input.dataset.pwToggle || input.closest(".password-wrapper")) return;
    input.dataset.pwToggle = "1";

    const wrap = document.createElement("span");
    wrap.className = "pw-wrap";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);

    const button = document.createElement("button");
    button.type = "button";
    button.className = "pw-toggle";
    setVisible(input, button, false);
    button.addEventListener("click", () => {
      setVisible(input, button, input.type === "password");
      input.focus();
    });
    wrap.appendChild(button);

    // Al limpiar el formulario, la contraseña vuelve a quedar oculta
    if (input.form) {
      input.form.addEventListener("reset", () => setVisible(input, button, false));
    }
  }

  function enhancePasswordInputs(root = document) {
    ensureStyle();
    root.querySelectorAll('input[type="password"]').forEach(enhance);
  }

  function start() {
    enhancePasswordInputs();
    new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) enhancePasswordInputs(node);
        });
      }
    }).observe(document.body, { childList: true, subtree: true });
  }

  window.enhancePasswordInputs = enhancePasswordInputs;
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
