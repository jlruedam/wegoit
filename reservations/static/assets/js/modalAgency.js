const agencyModal = document.getElementById("agencyModal");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.getElementById("closeModalBtn");
const agencyForm = agencyModal.querySelector('form'); // Get the form inside the modal
const modalAgencyTitle = agencyModal.querySelector('.modal__title');

// Función para resetear el formulario
function resetAgencyForm() {
    agencyForm.reset();
    agencyForm.action = "/agencies/create/"; // URL para crear nueva agencia
    if (modalAgencyTitle) {
        modalAgencyTitle.textContent = 'Agregar Agencia';
    }
    // Limpiar errores previos si los hubiera
    const errorDivs = agencyForm.querySelectorAll('.modal__form-group .errorlist'); // Assuming Django errorlist class
    errorDivs.forEach(div => div.remove());
}

// Abrir modal para crear agencia
openModalBtn.onclick = function() {
    resetAgencyForm();
    agencyModal.style.display = "block";
}

// Cerrar modal al hacer clic en la X
closeModalBtn.onclick = function() {
    agencyModal.style.display = "none";
    resetAgencyForm(); // Resetear el formulario al cerrar
}

// Cerrar modal al hacer clic fuera del contenido
window.onclick = function(event) {
    if (event.target == agencyModal) {
        agencyModal.style.display = "none";
        resetAgencyForm(); // Resetear el formulario al cerrar
    }
}

// Lógica para botones de edición de agencia
document.querySelectorAll('.editAgencyBtn').forEach(button => {
    button.addEventListener('click', function() {
        const agencyId = this.dataset.agencyId;
        const agencyName = this.dataset.agencyName;
        const agencyTaxId = this.dataset.agencyTaxId;
        const agencyPhone = this.dataset.agencyPhone;
        const agencyEmail = this.dataset.agencyEmail;

        if (modalAgencyTitle) {
            modalAgencyTitle.textContent = 'Editar Agencia';
        }
        if (agencyForm) {
            agencyForm.action = `/agencies/edit/${agencyId}/`; // Actualizar la acción del formulario
            // Asumiendo que los campos tienen IDs como 'id_name', 'id_tax_id', etc.
            const nameInput = document.getElementById('id_name');
            if (nameInput) nameInput.value = agencyName;

            const taxIdInput = document.getElementById('id_tax_id');
            if (taxIdInput) taxIdInput.value = agencyTaxId;

            const phoneInput = document.getElementById('id_phone');
            if (phoneInput) phoneInput.value = agencyPhone;

            const emailInput = document.getElementById('id_email');
            if (emailInput) emailInput.value = agencyEmail;
        }
        
        agencyModal.style.display = "block"; // Abrir el modal
    });
});

// Manejar el envío del formulario con AJAX
agencyForm.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevenir el envío normal del formulario

    const formData = new FormData(agencyForm);
    const url = agencyForm.action;
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
            agencyModal.style.display = "none"; // Cerrar modal
            resetAgencyForm(); // Resetear el formulario
            location.reload(); // Recargar la página para actualizar la lista de agencias
        } else {
            // Mostrar errores del formulario
            const errorDivs = agencyForm.querySelectorAll('.modal__form-group .errorlist');
            errorDivs.forEach(div => div.remove()); // Limpiar errores anteriores

            for (const fieldName in data.errors) {
                const fieldErrors = data.errors[fieldName];
                const fieldElement = document.getElementById(`id_${fieldName}`);
                if (fieldElement) {
                    const errorDiv = document.createElement('ul'); // Django errorlist is usually a ul
                    errorDiv.className = 'errorlist';
                    errorDiv.innerHTML = fieldErrors.map(error => `<li>${error}</li>`).join('');
                    fieldElement.parentNode.insertBefore(errorDiv, fieldElement.nextSibling);
                } else if (fieldName === '__all__') {
                    // Errores no relacionados con un campo específico
                    const nonFieldErrorsDiv = document.createElement('ul');
                    nonFieldErrorsDiv.className = 'errorlist';
                    nonFieldErrorsDiv.innerHTML = fieldErrors.map(error => `<li>${error}</li>`).join('');
                    agencyForm.prepend(nonFieldErrorsDiv);
                }
            }
            alert("Error al guardar la agencia. Revisa los campos.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error inesperado.');
    });
});
