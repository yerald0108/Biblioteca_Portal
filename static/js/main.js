document.addEventListener('DOMContentLoaded', function () {

  // ── CERRAR ALERTAS AUTOMÁTICAMENTE ───────────────────────
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.4s';
      setTimeout(function () { alert.remove(); }, 400);
    }, 4000);
  });

  // ── MENÚ DE USUARIO CON CLICK ─────────────────────────────
  const userAvatar   = document.querySelector('.user-avatar');
  const userDropdown = document.querySelector('.user-dropdown');
  const userMenu     = document.querySelector('.user-menu');

  if (userAvatar && userDropdown) {

    userAvatar.addEventListener('click', function (e) {
      e.stopPropagation();
      userDropdown.classList.toggle('abierto');
    });

    document.addEventListener('click', function (e) {
      if (userMenu && !userMenu.contains(e.target)) {
        userDropdown.classList.remove('abierto');
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        userDropdown.classList.remove('abierto');
      }
    });
  }

  // ── VALIDACIÓN DEL LADO DEL CLIENTE ──────────────────────
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      let valido = true;

      form.querySelectorAll('input, select, textarea').forEach(function (campo) {
        campo.style.borderColor = '';
        const errorPrevio = campo.parentElement.querySelector('.error-cliente');
        if (errorPrevio) errorPrevio.remove();

        if (campo.hasAttribute('required') && !campo.value.trim()) {
          valido = false;
          campo.style.borderColor = 'var(--rojo)';
          const error = document.createElement('div');
          error.className = 'error-texto error-cliente';
          error.style.cssText = 'font-size:12px; color:var(--rojo); margin-top:4px;';
          error.textContent = 'Este campo es obligatorio.';
          campo.parentElement.appendChild(error);
        }

        if (campo.type === 'email' && campo.value.trim()) {
          const emailValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(campo.value);
          if (!emailValido) {
            valido = false;
            campo.style.borderColor = 'var(--rojo)';
            const error = document.createElement('div');
            error.className = 'error-texto error-cliente';
            error.style.cssText = 'font-size:12px; color:var(--rojo); margin-top:4px;';
            error.textContent = 'Introduce un correo electrónico válido.';
            campo.parentElement.appendChild(error);
          }
        }

        if (campo.type === 'date' && campo.value && campo.dataset.minHoy !== undefined) {
          const hoy = new Date().toISOString().split('T')[0];
          if (campo.value <= hoy) {
            valido = false;
            campo.style.borderColor = 'var(--rojo)';
            const error = document.createElement('div');
            error.className = 'error-texto error-cliente';
            error.style.cssText = 'font-size:12px; color:var(--rojo); margin-top:4px;';
            error.textContent = 'La fecha debe ser posterior a hoy.';
            campo.parentElement.appendChild(error);
          }
        }
      });

      if (!valido) {
        e.preventDefault();
        const primerError = form.querySelector('[style*="var(--rojo)"]');
        if (primerError) {
          primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
          primerError.focus();
        }
      }
    });

    form.querySelectorAll('input, select, textarea').forEach(function (campo) {
      campo.addEventListener('input', function () {
        campo.style.borderColor = '';
        const error = campo.parentElement.querySelector('.error-cliente');
        if (error) error.remove();
      });
    });
  });

});