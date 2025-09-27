const modalTour = document.getElementById("modalTour");
const openModalTourBtn = document.getElementById("openModalTourBtn");
const closeModalTourBtn = document.getElementById("closeModalTourBtn");

// Abrir modal
openModalTourBtn.onclick = function() {
  modalTour.style.display = "flex";
};

// Cerrar modal al hacer clic en la X
closeModalTourBtn.onclick = function() {
  modalTour.style.display = "none";
};

// Cerrar modal al hacer clic fuera del contenido
window.onclick = function(event) {
  if (event.target === modalTour) {
    modalTour.style.display = "none";
  }
};

