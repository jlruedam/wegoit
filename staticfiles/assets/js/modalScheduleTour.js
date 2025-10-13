console.log('modalScheduleTour.js loaded');
const modalScheduleTour = document.getElementById("modalScheduleTour");
console.log('modalScheduleTour element:', modalScheduleTour);
const openModalScheduleTourBtn = document.getElementById("openModalScheduleTourBtn");
console.log('openModalScheduleTourBtn element:', openModalScheduleTourBtn);
const closeModalScheduleTourBtn = document.getElementById("closeModalScheduleTourBtn");
const scheduleForm = document.getElementById('scheduleForm');
const modalScheduleTourTitle = document.getElementById('modalScheduleTourTitle');

// Función para resetear el formulario
function resetScheduleForm() {
    scheduleForm.reset();
    scheduleForm.action = "/"; // URL para crear nuevo horario (home view handles POST)
    if (modalScheduleTourTitle) {
        modalScheduleTourTitle.textContent = 'Crear Horario de Tour';
    }
    // Limpiar errores previos si los hubiera
    const errorDivs = scheduleForm.querySelectorAll('.form__group .errorlist'); // Assuming Django errorlist class
    errorDivs.forEach(div => div.remove());

    // Re-apply initial data from the first tour if available (from home view context)
    const tourSelect = document.getElementById("id_tour");
    if (tourSelect && tourSelect.value) {
        const selected = window.tourDefaults[tourSelect.value];
        if (selected) {
            const capacityInput = document.getElementById("id_capacity");
            if (capacityInput) capacityInput.value = selected.capacity;

            const startTimeInput = document.getElementById("id_start_time");
            if (startTimeInput) startTimeInput.value = selected.start_time;
        }
    }
}

// Abrir modal para crear horario
if (openModalScheduleTourBtn) {
    openModalScheduleTourBtn.onclick = function() {
        console.log('openModalScheduleTourBtn clicked');
        resetScheduleForm();
        if (modalScheduleTour) {
            modalScheduleTour.style.display = "flex";
            console.log('modalScheduleTour display set to flex');
        } else {
            console.error('modalScheduleTour element not found when trying to open');
        }
    };
} else {
    console.error('openModalScheduleTourBtn element not found');
}

// Cerrar modal al hacer clic en la X
if (closeModalScheduleTourBtn) {
    closeModalScheduleTourBtn.onclick = function() {
        modalScheduleTour.style.display = "none";
        resetScheduleForm(); // Resetear el formulario al cerrar
    };
}

// Cerrar modal al hacer clic fuera del contenido
window.onclick = function(event) {
  if (event.target === modalScheduleTour) {
    modalScheduleTour.style.display = "none";
    resetScheduleForm(); // Resetear el formulario al cerrar
  }
};

// Manejar el envío del formulario con AJAX
if (scheduleForm) {
    scheduleForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevenir el envío normal del formulario

        const formData = new FormData(scheduleForm);
        const url = scheduleForm.action;
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
                modalScheduleTour.style.display = "none"; // Cerrar modal
                resetScheduleForm(); // Resetear el formulario
                location.reload(); // Recargar la página para actualizar la lista de horarios
            } else {
                // Mostrar errores del formulario
                const errorDivs = scheduleForm.querySelectorAll('.form__group .errorlist');
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
                        scheduleForm.prepend(nonFieldErrorsDiv);
                    }
                }
                alert("Error al guardar el horario. Revisa los campos.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ocurrió un error inesperado.');
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const tourSelect = document.getElementById("id_tour");
    const capacityInput = document.getElementById("id_capacity");
    const startTimeInput = document.getElementById("id_start_time");

    // Evento cuando cambia el Tour
    if (tourSelect) { // Check if tourSelect exists
        tourSelect.addEventListener("change", (e) => {
            const selected = window.tourDefaults[e.target.value];
            if (selected) {
                if (capacityInput && selected.capacity) { // Check if capacityInput exists
                    capacityInput.value = selected.capacity;
                }
                if (startTimeInput && selected.start_time) { // Check if startTimeInput exists
                    startTimeInput.value = selected.start_time;
                }
            }
        });
    }
});