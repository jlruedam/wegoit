window.addEventListener("load", () => {
  setTimeout(() => {
    if(document.getElementById("splash")){
      document.getElementById("splash").style.display = "none";
    }
    if(document.getElementById("contenido")){
      document.getElementById("contenido").style.display = "block";
    }
    
  }, 3000); // 3s (2s visible + 1s de animación fadeOut)
});
