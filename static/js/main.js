// Cerrar alertas automáticamente después de 4 segundos
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.4s';
      setTimeout(function () { alert.remove(); }, 400);
    }, 4000);
  });
});

// ── VALIDACIÓN DEL LADO DEL CLIENTE ─────────────────────────
document.addEventListener('DOMContentLoaded', function () {

  // Marcar campos requeridos vacíos al intentar enviar
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      let valido = true;

      form.querySelectorAll('input, select, textarea').forEach(function (campo) {
        // Limpiar error previo
        campo.style.borderColor = '';
        const errorPrevio = campo.parentElement.querySelector('.error-cliente');
        if (errorPrevio) errorPrevio.remove();

        // Validar requeridos
        if (campo.hasAttribute('required') && !campo.value.trim()) {
          valido = false;
          campo.style.borderColor = 'var(--rojo)';
          const error = document.createElement('div');
          error.className = 'error-texto error-cliente';
          error.style.fontSize = '12px';
          error.style.color = 'var(--rojo)';
          error.style.marginTop = '4px';
          error.textContent = 'Este campo es obligatorio.';
          campo.parentElement.appendChild(error);
        }

        // Validar email
        if (campo.type === 'email' && campo.value.trim()) {
          const emailValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(campo.value);
          if (!emailValido) {
            valido = false;
            campo.style.borderColor = 'var(--rojo)';
            const error = document.createElement('div');
            error.className = 'error-texto error-cliente';
            error.style.fontSize = '12px';
            error.style.color = 'var(--rojo)';
            error.style.marginTop = '4px';
            error.textContent = 'Introduce un correo electrónico válido.';
            campo.parentElement.appendChild(error);
          }
        }

        // Validar fechas mínimas
        if (campo.type === 'date' && campo.value) {
          const hoy = new Date().toISOString().split('T')[0];
          if (campo.dataset.minHoy !== undefined && campo.value <= hoy) {
            valido = false;
            campo.style.borderColor = 'var(--rojo)';
            const error = document.createElement('div');
            error.className = 'error-texto error-cliente';
            error.style.fontSize = '12px';
            error.style.color = 'var(--rojo)';
            error.style.marginTop = '4px';
            error.textContent = 'La fecha debe ser posterior a hoy.';
            campo.parentElement.appendChild(error);
          }
        }
      });

      if (!valido) {
        e.preventDefault();
        // Hacer scroll al primer error
        const primerError = form.querySelector('[style*="var(--rojo)"]');
        if (primerError) {
          primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
          primerError.focus();
        }
      }
    });

    // Limpiar error visual cuando el usuario empieza a escribir
    form.querySelectorAll('input, select, textarea').forEach(function (campo) {
      campo.addEventListener('input', function () {
        campo.style.borderColor = '';
        const error = campo.parentElement.querySelector('.error-cliente');
        if (error) error.remove();
      });
    });
  });
});