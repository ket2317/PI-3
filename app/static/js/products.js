let currentUser = null;
let branches = [];
let removeImage = false;

const MAX_IMAGE_SIZE = 2 * 1024 * 1024;
const IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

function showImagePreview(url) {
  const img = document.querySelector("#product-image-img");
  const preview = document.querySelector("#product-image-preview");
  img.hidden = !url;
  preview.classList.toggle("has-image", Boolean(url));
  if (url) {
    img.src = url;
  } else {
    img.removeAttribute("src");
  }
  document.querySelector("#product-image-remove").hidden = !url;
}

function showError(message) {
  showToast(message, "error");
}

function clearError() {}

function showSuccess(message) {
  showToast(message, "success");
}

function clearSuccess() {}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",...options,
  });

  const data = await response.json().catch(() => ({}));
  
  if (response.status === 401)
    { window.location.href = "/login";
      throw new Error("Debes iniciar sesión");
    }
    
    if (!response.ok) {
      throw new Error(errorDetail(data.detail) || `Error ${response.status}`);
    }
    
    return data;
  }

  function getBranchName(branchId) {
    const branch = branches.find((item) => item.id === branchId);
    return branch ? branch.nombre : `Sucursal ${branchId}`;
  }
  
  function resetForm() {
    document.querySelector("#product-form").reset();
    document.querySelector("#product-id").value = "";
    document.querySelector("#product-tax").value = "0.16";
    document.querySelector("#product-modal-title").textContent =
    "Añadir producto";
    document.querySelector("#product-submit").textContent =
    "Guardar producto";
    document.querySelector("#product-image").value = "";
    removeImage = false;
    showImagePreview(null);

    const branchSelect = document.querySelector("#product-branch-id");
    const filterValue = document.querySelector("#product-filter-branch").value;
    if (currentUser && currentUser.rol === "GERENTE") {
      branchSelect.value = currentUser.sucursal_id;
    } else if (filterValue) {
      branchSelect.value = filterValue;
    }
    clearError();
  }
  
  async function loadCurrentUser() {
    currentUser = await apiRequest("/auth/me");
  }
  
  async function loadBranches() {
    branches = await apiRequest("/sucursales/");

    const select = document.querySelector("#product-branch-id");
    const filter = document.querySelector("#product-filter-branch");
    select.innerHTML = "";
    filter.innerHTML = `<option value="">Todas las sucursales</option>`;
    
    branches.forEach((branch) => {
      const option = document.createElement("option");
      option.value = branch.id;
      option.textContent = branch.nombre;
      select.appendChild(option);
      filter.appendChild(option.cloneNode(true));
    });

  if (currentUser.rol === "GERENTE") {
    select.value = currentUser.sucursal_id;
    select.disabled = true;
  }

  // Solo el administrador ve varias sucursales
  filter.hidden = currentUser.rol !== "ADMIN";
}

async function loadCategories() {
  const categories = await apiRequest("/categorias/");
  const select = document.querySelector("#product-category-id");
  
  select.innerHTML = `<option value="">Sin categoría</option>`;
  
  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category.id;
    option.textContent = category.nombre;
    select.appendChild(option);
  });
}

async function loadProducts() {
  const branchId = Number(
    document.querySelector("#product-filter-branch").value
  );

  let url = "/productos/";

  if (currentUser.rol === "ADMIN" && branchId) {
    url += `?sucursal_id=${branchId}`;
  }

  const products = await apiRequest(withSearch(url));
  const body = document.querySelector("#products-body");

  body.innerHTML = "";
  document.querySelector("#products-count").textContent = products.length;

  if (products.length === 0) {
    body.innerHTML = `
      <tr data-empty-state><td colspan="5" class="empty-state">
        ${emptyMessage("Aún no hay productos. Usa “Añadir producto” para registrar el primero.")}
      </td></tr>
    `;
  }

  products.forEach((product) => {
    const row = document.createElement("tr");

    const thumb = product.imagen_url
      ? `<img class="product-thumb" src="${product.imagen_url}" alt="" loading="lazy">`
      : `<span class="product-thumb product-thumb-empty"><svg class="icon icon-sm" viewBox="0 0 24 24"><path d="M21 8 12 3 3 8l9 5 9-5Z"/><path d="M3 8v8l9 5 9-5V8"/></svg></span>`;

    row.innerHTML = `
      <td class="cell-strong">
        <div class="product-cell">
          ${thumb}
          <div>
            ${product.nombre}
            <span class="cell-sub">Código ${product.codigo}</span>
          </div>
        </div>
      </td>
      <td>${getBranchName(product.sucursal_id)}</td>
      <td>$${Number(product.precio).toFixed(2)}</td>
      <td>${Math.round(Number(product.iva) * 100)}%</td>
      <td class="cell-actions"></td>
    `;

    const editButton = iconButton("edit", "edit", "Editar");
    editButton.addEventListener("click", () => editProduct(product));

    const deleteButton = iconButton("delete", "disable", "Desactivar");
    deleteButton.addEventListener("click", () => deactivateProduct(product));

    row.lastElementChild.append(editButton, deleteButton);

    body.appendChild(row);
  });
}

function editProduct(product) {
  document.querySelector("#product-id").value = product.id;
  document.querySelector("#product-branch-id").value =
    product.sucursal_id;
  document.querySelector("#product-category-id").value =
    product.categoria_id || "";
  document.querySelector("#product-code").value = product.codigo;
  document.querySelector("#product-name").value = product.nombre;
  document.querySelector("#product-price").value = product.precio;
  document.querySelector("#product-tax").value = product.iva;
  document.querySelector("#product-image").value = "";
  removeImage = false;
  showImagePreview(product.imagen_url);
  document.querySelector("#product-modal-title").textContent =
    "Editar producto";
  document.querySelector("#product-submit").textContent =
    "Guardar cambios";
  openModal("product-modal");
}

async function deactivateProduct(product) {
  const confirmed = window.confirm(
    `¿Desactivar el producto "${product.nombre}"?`
  );
  
  if (!confirmed) {
    return;
  }
  
  try {
    clearError();
    clearSuccess();
    
    await apiRequest(`/productos/${product.id}`, {
      method: "DELETE",
    });
    
    showSuccess("Producto desactivado correctamente");
    await loadProducts();
  } catch (error) {
    showError(error.message);
  }
}

document.querySelector("#product-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    
    const productId = document.querySelector("#product-id").value;
    const categoryValue =
      document.querySelector("#product-category-id").value;
    
    const payload = {
      sucursal_id: Number(
        document.querySelector("#product-branch-id").value
      ),
      codigo: document.querySelector("#product-code").value.trim(),
      nombre: document.querySelector("#product-name").value.trim(),
      precio: document.querySelector("#product-price").value,
      iva: document.querySelector("#product-tax").value,
      categoria_id: categoryValue ? Number(categoryValue) : null,
    };
    
    try {
      clearError();
      clearSuccess();
      
      const url = productId
        ? `/productos/${productId}`
        : "/productos/";
        
      const saved = await apiRequest(url, {
        method: productId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const file = document.querySelector("#product-image").files[0];
      if (file) {
        const formData = new FormData();
        formData.append("archivo", file);
        await apiRequest(`/productos/${saved.id}/imagen`, {
          method: "PUT",
          body: formData,
        });
      } else if (removeImage && saved.imagen_url) {
        await apiRequest(`/productos/${saved.id}/imagen`, {
          method: "DELETE",
        });
      }

      showSuccess(
        productId
        ? "Producto actualizado correctamente"
        : "Producto creado correctamente"
      );

      closeModal("product-modal");
      await loadProducts();
    } catch (error) {
      showError(error.message);
    }
  });

document.querySelector("#product-image")
  .addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file) {
      return;
    }
    if (!IMAGE_TYPES.includes(file.type)) {
      showError("Solo se permiten imágenes JPG, PNG o WEBP");
      event.target.value = "";
      return;
    }
    if (file.size > MAX_IMAGE_SIZE) {
      showError("La imagen no puede pesar más de 2 MB");
      event.target.value = "";
      return;
    }
    removeImage = false;
    showImagePreview(URL.createObjectURL(file));
  });

document.querySelector("#product-image-remove")
  .addEventListener("click", () => {
    document.querySelector("#product-image").value = "";
    removeImage = true;
    showImagePreview(null);
  });

document.querySelector("#product-new")
  .addEventListener("click", () => {
    resetForm();
    openModal("product-modal");
  });

document.querySelector("#product-modal")
  .addEventListener("close", resetForm);

document.querySelector("#product-filter-branch")
  .addEventListener("change", async () => {
    try {
      await loadProducts();
    } catch (error) {
      showError(error.message);
    }
  });

(async () => {
  try {
    await loadCurrentUser();
    await loadBranches();
    await loadCategories();
    await loadProducts();
    onSearch(loadProducts);
  } catch (error) {
    showError(error.message);
  }
})();