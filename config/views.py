from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from biblioteca.models import Libro, Prestamo, Tesis, Profesor

@login_required
def home(request):
    context = {
        'total_libros':    Libro.objects.count(),
        'total_prestamos': Prestamo.objects.filter(estado='activo').count(),
        'total_tesis':     Tesis.objects.filter(disponible=True).count(),
        'total_profesores':Profesor.objects.filter(activo=True).count(),
    }
    return render(request, 'home.html', context)