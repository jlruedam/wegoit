window.addEventListener("load", () => {
  setTimeout(() => {
    document.getElementById("splash").style.display = "none";
    document.getElementById("contenido").style.display = "block";
  }, 3000); // 3s (2s visible + 1s de animación fadeOut)
});
