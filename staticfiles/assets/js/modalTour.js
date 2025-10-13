const modalTour = document.getElementById("modalTour");
const openModalTourBtn = document.getElementById("openModalTourBtn");
const closeModalTourBtn = document.getElementById("closeModalTourBtn");
const tourForm = document.getElementById('tourForm');
const modalTourTitle = document.getElementById('modalTourTitle');

// Función para resetear el formulario
function resetTourForm() {
    tourForm.reset();
    tourForm.action = "/tours/"; // URL para crear nuevo tour
    if (modalTourTitle) {
        modalTourTitle.textContent = 'Crear Tour';
    }
    // Limpiar errores previos si los hubiera
    const errorDivs = tourForm.querySelectorAll('.form__error');
    errorDivs.forEach(div => div.remove());
}

// Abrir modal para crear tour
openModalTourBtn.onclick = function() {
    resetTourForm();
    modalTour.style.display = "flex";
};

// Cerrar modal al hacer clic en la X
closeModalTourBtn.onclick = function() {
    modalTour.style.display = "none";
    resetTourForm(); // Resetear el formulario al cerrar
};

// Cerrar modal al hacer clic fuera del contenido
window.onclick = function(event) {
    if (event.target === modalTour) {
        modalTour.style.display = "none";
        resetTourForm(); // Resetear el formulario al cerrar
    }
};

// Lógica para botones de edición de tour
document.querySelectorAll('.editTourBtn').forEach(button => {
    button.addEventListener('click', function() {
        const tourId = this.dataset.tourId;
        const tourName = this.dataset.tourName;
        const tourDescription = this.dataset.tourDescription;
        const tourBasePrice = this.dataset.tourBasePrice;
        const tourDefaultCapacity = this.dataset.tourDefaultCapacity;
        const tourActive = this.dataset.tourActive === 'true';

        if (modalTourTitle) {
            modalTourTitle.textContent = 'Editar Tour';
        }
        if (tourForm) {
            tourForm.action = `/tours/edit/${tourId}/`; // Actualizar la acción del formulario

            const nameInput = document.getElementById('id_tour_name');
            if (nameInput) nameInput.value = tourName;

            const descriptionInput = document.getElementById('id_description');
            if (descriptionInput) descriptionInput.value = tourDescription;

            const basePriceInput = document.getElementById('id_base_price');
            if (basePriceInput) basePriceInput.value = tourBasePrice;

            const defaultCapacityInput = document.getElementById('id_default_capacity');
            if (defaultCapacityInput) defaultCapacityInput.value = tourDefaultCapacity;

            const activeInput = document.getElementById('id_active');
            if (activeInput) activeInput.checked = tourActive;
        }
        
        modalTour.style.display = "flex"; // Abrir el modal
    });
});

// Manejar el envío del formulario con AJAX
tourForm.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevenir el envío normal del formulario

    const formData = new FormData(tourForm);
    const url = tourForm.action;
    const method = 'POST';

    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message); // Mostrar mensaje de éxito
            modalTour.style.display = "none"; // Cerrar modal
            resetTourForm(); // Resetear el formulario
            location.reload(); // Recargar la página para actualizar la lista de tours
        } else {
            // Mostrar errores del formulario
            const errorDivs = tourForm.querySelectorAll('.form__error');
            errorDivs.forEach(div => div.remove()); // Limpiar errores anteriores

            for (const fieldName in data.errors) {
                const fieldErrors = data.errors[fieldName];
                const fieldElement = document.getElementById(`id_${fieldName}`);
                if (fieldElement) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'form__error';
                    errorDiv.innerHTML = fieldErrors.map(error => `<p>${error}</p>`).join('');
                    fieldElement.parentNode.insertBefore(errorDiv, fieldElement.nextSibling);
                } else if (fieldName === '__all__') {
                    // Errores no relacionados con un campo específico
                    const nonFieldErrorsDiv = document.createElement('div');
                    nonFieldErrorsDiv.className = 'form__error';
                    nonFieldErrorsDiv.innerHTML = fieldErrors.map(error => `<p>${error}</p>`).join('');
                    tourForm.prepend(nonFieldErrorsDiv);
                }
            }
            alert("Error al guardar el tour. Revisa los campos.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error inesperado.');
    });
});