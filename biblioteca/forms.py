from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Libro, Ejemplar, Categoria, Prestamo, Tesis, Profesor, Recurso, PerfilUsuario
import datetime

class LibroForm(forms.ModelForm):
    class Meta:
        model  = Libro
        fields = ['titulo', 'autor', 'editorial', 'anio', 'isbn',
                  'categoria', 'descripcion', 'portada']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class EjemplarForm(forms.ModelForm):
    class Meta:
        model  = Ejemplar
        fields = ['codigo', 'estado', 'ubicacion', 'notas']
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class BusquedaForm(forms.Form):
    q         = forms.CharField(required=False, label='Buscar')
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False, empty_label='Todas las categorías'
    )
    estado = forms.ChoiceField(
        choices=[('', 'Cualquier estado'),
                 ('disponible', 'Disponible'),
                 ('prestado',   'Prestado'),
                 ('reservado',  'Reservado')],
        required=False
    )

class PrestamoForm(forms.ModelForm):
    class Meta:
        model  = Prestamo
        fields = ['ejemplar', 'usuario', 'fecha_devolucion', 'notas']
        widgets = {
            'fecha_devolucion': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'
            ),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar ejemplares disponibles
        from .models import Ejemplar
        self.fields['ejemplar'].queryset = Ejemplar.objects.filter(
            estado='disponible'
        ).select_related('libro')
        # Fecha mínima: mañana
        self.fields['fecha_devolucion'].initial = (
            datetime.date.today() + datetime.timedelta(days=7)
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_fecha_devolucion(self):
        fecha = self.cleaned_data.get('fecha_devolucion')
        if fecha and fecha <= datetime.date.today():
            raise forms.ValidationError('La fecha debe ser posterior a hoy.')
        return fecha

class TesisForm(forms.ModelForm):
    class Meta:
        model  = Tesis
        fields = ['titulo', 'autor', 'tutor', 'anio', 'tipo',
                  'area', 'resumen', 'archivo_pdf', 'disponible']
        widgets = {
            'resumen': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo:
            if not archivo.name.endswith('.pdf'):
                raise forms.ValidationError('Solo se permiten archivos PDF.')
            if archivo.size > 20 * 1024 * 1024:  # 20 MB
                raise forms.ValidationError('El archivo no puede superar 20 MB.')
        return archivo

class ProfesorForm(forms.ModelForm):
    class Meta:
        model  = Profesor
        fields = ['nombre', 'apellidos', 'categoria', 'ambito', 'pais',
                  'especialidad', 'biografia', 'email', 'foto', 'activo']
        widgets = {
            'biografia': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
                
class RecursoForm(forms.ModelForm):
    class Meta:
        model  = Recurso
        fields = ['titulo', 'tipo', 'descripcion', 'archivo',
                  'url_video', 'imagen', 'publicado', 'destacado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned = super().clean()
        tipo    = cleaned.get('tipo')
        archivo = cleaned.get('archivo')
        video   = cleaned.get('url_video')
        if tipo == 'video' and not video and not archivo:
            raise forms.ValidationError(
                'Un recurso de tipo Video debe tener una URL o un archivo.'
            )
        return cleaned
    
class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, label='Nombre')
    last_name  = forms.CharField(max_length=150, required=False, label='Apellidos')
    email      = forms.EmailField(required=False, label='Correo electrónico')

    class Meta:
        model  = PerfilUsuario
        fields = ['carnet', 'telefono', 'foto']

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['first_name'].initial = usuario.first_name
            self.fields['last_name'].initial  = usuario.last_name
            self.fields['email'].initial      = usuario.email
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class GestionUsuarioForm(forms.ModelForm):
    """Solo para el bibliotecario: cambia rol y datos básicos."""
    class Meta:
        model  = PerfilUsuario
        fields = ['rol', 'carnet', 'telefono']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True,  label='Nombre')
    last_name  = forms.CharField(max_length=150, required=True,  label='Apellidos')
    email      = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['username'].help_text = 'Solo letras, números y @/./+/-/_'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres.'
        self.fields['password2'].help_text = ''
            