/* Archivo: static/main.js */

// Esperamos a que todo el HTML cargue antes de ejecutar el código
document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Buscamos TODOS los elementos que tengan la clase 'btn-eliminar'
    const botonesEliminar = document.querySelectorAll('.btn-eliminar');

    // 2. A cada botón le asignamos un "Escucha" (Listener)
    botonesEliminar.forEach(boton => {
        boton.addEventListener('click', function(evento) {
            
            // 3. Mostramos la alerta de confirmación
            const confirmacion = confirm("¿Estás seguro de eliminar este libro permanentemente?");

            // 4. Si el usuario dice "Cancelar" (false)...
            if (!confirmacion) {
                // ... detenemos el enlace. El navegador NO irá a la URL de borrar.
                evento.preventDefault();
            }
            // Si dice "Aceptar", no hacemos nada y el enlace funciona normal.
        });
    });

});