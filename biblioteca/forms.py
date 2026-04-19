from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import (Libro, Ejemplar, Categoria, Prestamo, Tesis,
                     Profesor, Recurso, PerfilUsuario,
                     SolicitudPrestamo, RenovacionPrestamo)
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
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'


class EjemplarForm(forms.ModelForm):
    class Meta:
        model  = Ejemplar
        fields = ['codigo', 'estado', 'ubicacion', 'notas']
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'


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
        self.fields['ejemplar'].queryset = Ejemplar.objects.filter(
            estado='disponible'
        ).select_related('libro')
        self.fields['fecha_devolucion'].initial = (
            datetime.date.today() + datetime.timedelta(days=7)
        )
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'
        self.fields['fecha_devolucion'].widget.attrs['data-min-hoy'] = ''

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
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo:
            if not archivo.name.endswith('.pdf'):
                raise forms.ValidationError('Solo se permiten archivos PDF.')
            if archivo.size > 20 * 1024 * 1024:
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
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'


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
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'

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
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class GestionUsuarioForm(forms.ModelForm):
    class Meta:
        model  = PerfilUsuario
        fields = ['rol', 'carnet', 'telefono']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class RegistroUsuarioForm(UserCreationForm):
    ROL_OPCIONES = [
        ('estudiante', 'Estudiante'),
        ('profesor',   'Profesor'),
    ]

    first_name       = forms.CharField(max_length=150, required=True,
                                        label='Nombre')
    last_name        = forms.CharField(max_length=150, required=True,
                                        label='Apellidos')
    email            = forms.EmailField(required=True,
                                         label='Correo electrónico')
    rol_solicitado   = forms.ChoiceField(
        choices=ROL_OPCIONES,
        required=True,
        label='Soy...',
    )
    motivo_solicitud = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Información adicional',
        help_text='Opcional. Matrícula, departamento u otra información relevante.'
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = 'form-control'
            if field.required and name not in ['rol_solicitado']:
                field.widget.attrs['required'] = 'required'
        self.fields['username'].help_text = 'Solo letras, números y @/./+/-/_'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres.'
        self.fields['password2'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email


class SolicitudPrestamoForm(forms.ModelForm):
    class Meta:
        model   = SolicitudPrestamo
        fields  = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Opcional: explica para qué necesitas el libro...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mensaje'].required = False
        self.fields['mensaje'].widget.attrs['class'] = 'form-control'


class AprobarSolicitudForm(forms.Form):
    ejemplar = forms.ModelChoiceField(
        queryset=None,
        label='Ejemplar a prestar',
        empty_label='Selecciona un ejemplar...'
    )
    fecha_devolucion = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha límite de devolución'
    )
    respuesta = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        label='Mensaje al usuario (opcional)'
    )

    def __init__(self, *args, **kwargs):
        libro = kwargs.pop('libro', None)
        super().__init__(*args, **kwargs)
        if libro:
            self.fields['ejemplar'].queryset = Ejemplar.objects.filter(
                libro=libro, estado='disponible'
            )
        self.fields['fecha_devolucion'].initial = (
            datetime.date.today() + datetime.timedelta(days=7)
        )
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'
        self.fields['fecha_devolucion'].widget.attrs['data-min-hoy'] = ''

    def clean_fecha_devolucion(self):
        fecha = self.cleaned_data.get('fecha_devolucion')
        if fecha and fecha <= datetime.date.today():
            raise forms.ValidationError('La fecha debe ser posterior a hoy.')
        return fecha


class RechazarSolicitudForm(forms.Form):
    respuesta = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Motivo del rechazo'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['respuesta'].widget.attrs['class'] = 'form-control'
        if self.fields['respuesta'].required:
            self.fields['respuesta'].widget.attrs['required'] = 'required'


class RenovacionForm(forms.ModelForm):
    class Meta:
        model   = RenovacionPrestamo
        fields  = ['dias_solicitados', 'motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'
        self.fields['dias_solicitados'].widget.attrs['min'] = 1
        self.fields['dias_solicitados'].widget.attrs['max'] = 30

    def clean_dias_solicitados(self):
        dias = self.cleaned_data.get('dias_solicitados')
        if dias and (dias < 1 or dias > 30):
            raise forms.ValidationError(
                'Puedes solicitar entre 1 y 30 días de extensión.'
            )
        return dias


class AprobarRenovacionForm(forms.Form):
    nueva_fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Nueva fecha de devolución'
    )
    respuesta = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        label='Mensaje al usuario (opcional)'
    )

    def __init__(self, *args, **kwargs):
        prestamo = kwargs.pop('prestamo', None)
        super().__init__(*args, **kwargs)
        if prestamo:
            self.fields['nueva_fecha'].initial = (
                prestamo.fecha_devolucion + datetime.timedelta(days=7)
            )
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'
        self.fields['nueva_fecha'].widget.attrs['data-min-hoy'] = ''

    def clean_nueva_fecha(self):
        fecha = self.cleaned_data.get('nueva_fecha')
        if fecha and fecha <= datetime.date.today():
            raise forms.ValidationError(
                'La nueva fecha debe ser posterior a hoy.'
            )
        return fecha


class RechazarRenovacionForm(forms.Form):
    respuesta = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Motivo del rechazo'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['respuesta'].widget.attrs['class'] = 'form-control'
        if self.fields['respuesta'].required:
            self.fields['respuesta'].widget.attrs['required'] = 'required'


class CategoriaForm(forms.ModelForm):
    class Meta:
        model  = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'