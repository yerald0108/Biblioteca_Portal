from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from biblioteca.models import Libro, Prestamo, Tesis, Profesor
from biblioteca.forms import RegistroUsuarioForm


@login_required
def home(request):
    context = {
        'total_libros':     Libro.objects.count(),
        'total_prestamos':  Prestamo.objects.filter(estado='activo').count(),
        'total_tesis':      Tesis.objects.filter(disponible=True).count(),
        'total_profesores': Profesor.objects.filter(activo=True).count(),
    }
    return render(request, 'home.html', context)


def registro(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegistroUsuarioForm(request.POST or None)
    if form.is_valid():
        usuario = form.save()
        login(request, usuario)
        return redirect('home')
    return render(request, 'registration/registro.html', {'form': form})