const modalScheduleTour = document.getElementById("modalScheduleTour");
const openModalScheduleTourBtn = document.getElementById("openModalScheduleTourBtn");
const closeModalScheduleTourBtn = document.getElementById("closeModalScheduleTourBtn");

// Abrir modal
openModalScheduleTourBtn.onclick = function() {
  modalScheduleTour.style.display = "flex";
};

// Cerrar modal al hacer clic en la X
closeModalScheduleTourBtn.onclick = function() {
  modalScheduleTour.style.display = "none";
};

// Cerrar modal al hacer clic fuera del contenido
window.onclick = function(event) {
  if (event.target === modalScheduleTour) {
    modalScheduleTour.style.display = "none";
  }
};


