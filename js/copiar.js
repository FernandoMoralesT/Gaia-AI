/* Botón "Copiar" del hash SHA-256.
   Sin JavaScript el botón sigue oculto (atributo hidden) y el hash se puede seleccionar a mano. */
(function () {
  if (!navigator.clipboard) return;
  document.querySelectorAll('[data-copiar]').forEach(function (boton) {
    var destino = document.getElementById(boton.dataset.copiar);
    if (!destino) return;
    boton.hidden = false;
    boton.addEventListener('click', function () {
      navigator.clipboard.writeText(destino.textContent.trim()).then(function () {
        boton.textContent = 'Copiado';
        setTimeout(function () { boton.textContent = 'Copiar'; }, 2000);
      });
    });
  });
})();
