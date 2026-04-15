from django import forms
from .models import Libro, Ejemplar, Categoria, Prestamo, Tesis, Profesor, Recurso
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