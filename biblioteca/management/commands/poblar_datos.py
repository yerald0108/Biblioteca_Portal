from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from biblioteca.models import (
    Categoria, Libro, Ejemplar, Prestamo,
    Tesis, Profesor, Recurso, PerfilUsuario
)
from django.utils import timezone
import datetime
import random


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de prueba...')

        # ── USUARIOS ──────────────────────────────────────────
        usuarios_data = [
            {'username': 'bibliotecario1', 'first_name': 'María',    'last_name': 'González',  'email': 'maria@biblioteca.cu',   'is_staff': True},
            {'username': 'estudiante1',    'first_name': 'Carlos',   'last_name': 'Rodríguez', 'email': 'carlos@estudiante.cu',  'is_staff': False},
            {'username': 'estudiante2',    'first_name': 'Ana',      'last_name': 'Fuentes',   'email': 'ana@estudiante.cu',     'is_staff': False},
            {'username': 'estudiante3',    'first_name': 'Luis',     'last_name': 'Pérez',     'email': 'luis@estudiante.cu',    'is_staff': False},
            {'username': 'profesor1',      'first_name': 'Jorge',    'last_name': 'Mendoza',   'email': 'jorge@profesor.cu',     'is_staff': False},
            {'username': 'visitante1',     'first_name': 'Roberto',  'last_name': 'Lima',      'email': 'roberto@visita.cu',     'is_staff': False},
        ]

        usuarios = {}
        for data in usuarios_data:
            u, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name':  data['last_name'],
                    'email':      data['email'],
                    'is_staff':   data['is_staff'],
                }
            )
            if created:
                u.set_password('prueba1234')
                u.save()
            usuarios[data['username']] = u

        # Asignar roles a perfiles
        roles = {
            'bibliotecario1': 'bibliotecario',
            'estudiante1':    'estudiante',
            'estudiante2':    'estudiante',
            'estudiante3':    'estudiante',
            'profesor1':      'profesor',
            'visitante1':     'visitante',
        }
        carnets = {
            'estudiante1': 'EST-2024-001',
            'estudiante2': 'EST-2024-002',
            'estudiante3': 'EST-2024-003',
            'profesor1':   'PRF-2024-001',
        }
        for username, rol in roles.items():
            perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuarios[username])
            perfil.rol    = rol
            perfil.carnet = carnets.get(username, '')
            perfil.save()

        self.stdout.write('  Usuarios creados.')

        # ── CATEGORÍAS ────────────────────────────────────────
        cats_data = [
            'Ingeniería Civil',
            'Informática',
            'Matemática',
            'Derecho',
            'Urbanismo',
            'Medio Ambiente',
            'Historia',
            'Literatura',
        ]
        categorias = {}
        for nombre in cats_data:
            c, _ = Categoria.objects.get_or_create(nombre=nombre)
            categorias[nombre] = c

        self.stdout.write('  Categorías creadas.')

        # ── LIBROS ────────────────────────────────────────────
        libros_data = [
            ('Análisis Matemático II',                  'Boris Demidovich',       'MIR',          1991, '978-5-03-000000-1', 'Matemática'),
            ('Algoritmos y Estructuras de Datos',       'Thomas Cormen',          'MIT Press',    2009, '978-0-26-203293-7', 'Informática'),
            ('Urbanismo y Planificación Territorial',   'Fernández Torres',       'ISPJAE',       2005, None,                'Urbanismo'),
            ('Derecho Constitucional Cubano',           'García Hernández',       'Félix Varela', 2018, '978-9-59-209000-3', 'Derecho'),
            ('Mecánica de Suelos',                      'Karl Terzaghi',          'Limusa',       1996, '978-9-68-180000-2', 'Ingeniería Civil'),
            ('Gestión Ambiental Urbana',                'Pérez Valdivia',         'UNAH',         2015, None,                'Medio Ambiente'),
            ('Historia de Cuba',                        'Julio Le Riverend',      'Ciencias Soc.',1985, None,                'Historia'),
            ('Cien Años de Soledad',                    'Gabriel García Márquez', 'Sudamericana', 1967, '978-0-06-088328-7', 'Literatura'),
            ('Inteligencia Artificial',                 'Stuart Russell',         'Pearson',      2020, '978-0-13-461099-3', 'Informática'),
            ('Resistencia de Materiales',               'Timoshenko',             'Montaner',     1957, None,                'Ingeniería Civil'),
            ('Cálculo Diferencial e Integral',          'Piskunov',               'MIR',          1977, None,                'Matemática'),
            ('Redes de Computadoras',                   'Andrew Tanenbaum',       'Pearson',      2011, '978-0-13-212695-3', 'Informática'),
        ]

        libros = []
        for titulo, autor, editorial, anio, isbn, cat in libros_data:
            libro, _ = Libro.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'autor':      autor,
                    'editorial':  editorial,
                    'anio':       anio,
                    'isbn':       isbn,
                    'categoria':  categorias[cat],
                    'descripcion': f'Libro de referencia para la especialidad de {cat}.',
                }
            )
            libros.append(libro)

        self.stdout.write('  Libros creados.')

        # ── EJEMPLARES ────────────────────────────────────────
        estados_posibles = ['disponible', 'disponible', 'disponible', 'prestado', 'reservado']
        for i, libro in enumerate(libros):
            num_ejemplares = random.randint(2, 4)
            for j in range(num_ejemplares):
                codigo = f'EJ-{str(i+1).zfill(3)}-{str(j+1).zfill(2)}'
                Ejemplar.objects.get_or_create(
                    codigo=codigo,
                    defaults={
                        'libro':     libro,
                        'estado':    'disponible',
                        'ubicacion': f'Estante {chr(65 + i % 8)}, Fila {j + 1}',
                    }
                )

        self.stdout.write('  Ejemplares creados.')

        # ── PRÉSTAMOS ─────────────────────────────────────────
        hoy = timezone.now().date()
        ejemplares_disponibles = list(
            Ejemplar.objects.filter(estado='disponible')[:6]
        )
        prestamos_config = [
            # (usuario,       días_desde_hoy, estado)
            ('estudiante1',  -5,  'vencido'),
            ('estudiante2',  -1,  'vencido'),
            ('estudiante3',   1,  'activo'),
            ('estudiante1',   5,  'activo'),
            ('profesor1',     3,  'activo'),
            ('visitante1',  -10,  'vencido'),
        ]

        bibliotecario = usuarios['bibliotecario1']
        for idx, (username, dias, estado) in enumerate(prestamos_config):
            if idx >= len(ejemplares_disponibles):
                break
            ejemplar = ejemplares_disponibles[idx]
            usuario  = usuarios[username]
            fecha_dev = hoy + datetime.timedelta(days=dias)

            p, created = Prestamo.objects.get_or_create(
                ejemplar=ejemplar,
                usuario=usuario,
                defaults={
                    'fecha_devolucion': fecha_dev,
                    'estado':           estado,
                    'registrado_por':   bibliotecario,
                }
            )
            if created and estado in ('activo', 'vencido'):
                ejemplar.estado = 'prestado'
                ejemplar.save()

        self.stdout.write('  Préstamos creados.')

        # ── TESIS ─────────────────────────────────────────────
        tesis_data = [
            ('Optimización de redes de transporte urbano en municipios cubanos',
             'Pedro Álvarez Ruiz',       'Dr. Manuel Reyes',  2023, 'licenciatura', 'Ingeniería Civil'),
            ('Gestión de residuos sólidos en zonas periurbanas',
             'Yanet Cruz Morales',       'Dra. Ana Ferrer',   2022, 'maestria',     'Medio Ambiente'),
            ('Aplicaciones de IA en ordenamiento territorial',
             'Reinaldo Sosa López',      'Dr. Jorge Mendoza', 2024, 'licenciatura', 'Informática'),
            ('Impacto del cambio climático en la planificación urbana',
             'Lisandra Pérez Gómez',     'Dr. Manuel Reyes',  2023, 'doctorado',    'Urbanismo'),
            ('Sistemas de información geográfica para gestión municipal',
             'Orlando Fuentes Díaz',     'Dra. Ana Ferrer',   2021, 'maestria',     'Informática'),
            ('Análisis estructural de edificaciones históricas en La Habana',
             'Caridad Valdés Hernández', 'Dr. Jorge Mendoza', 2022, 'licenciatura', 'Ingeniería Civil'),
        ]

        for titulo, autor, tutor, anio, tipo, area in tesis_data:
            Tesis.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'autor':      autor,
                    'tutor':      tutor,
                    'anio':       anio,
                    'tipo':       tipo,
                    'area':       area,
                    'resumen':    f'Esta tesis aborda aspectos fundamentales de {area} con aplicaciones prácticas en el contexto cubano.',
                    'disponible': True,
                }
            )

        self.stdout.write('  Tesis creadas.')

        # ── PROFESORES ────────────────────────────────────────
        profesores_data = [
            ('Manuel',   'Reyes Torres',    'titular',   'nacional',      '',       'Ingeniería Hidráulica'),
            ('Ana',      'Luisa Ferrer',    'titular',   'nacional',      '',       'Urbanismo'),
            ('Jorge',    'Mendoza Castillo','titular',   'internacional', 'México', 'Ciencias Ambientales'),
            ('Rosa',     'Pérez Vila',      'auxiliar',  'nacional',      '',       'Matemática Aplicada'),
            ('Antonio',  'Gómez Sánchez',   'titular',   'internacional', 'España', 'Derecho Constitucional'),
            ('Miriam',   'Castro Díaz',     'asistente', 'nacional',      '',       'Informática'),
        ]

        for nombre, apellidos, cat, ambito, pais, esp in profesores_data:
            Profesor.objects.get_or_create(
                nombre=nombre,
                apellidos=apellidos,
                defaults={
                    'categoria':   cat,
                    'ambito':      ambito,
                    'pais':        pais,
                    'especialidad':esp,
                    'biografia':   f'Profesor {cat} con amplia experiencia en {esp}. Ha publicado numerosos trabajos de investigación en revistas especializadas.',
                    'activo':      True,
                }
            )

        self.stdout.write('  Profesores creados.')

        # ── RECURSOS ──────────────────────────────────────────
        admin_user = User.objects.filter(is_staff=True).first()
        recursos_data = [
            ('Nueva adquisición: 15 títulos de ingeniería estructural', 'novedad',
             'La biblioteca incorpora nuevos títulos especializados en ingeniería estructural y sísmica, disponibles para préstamo inmediato.', True),
            ('Tutorial: Uso del repositorio y descarga de tesis',       'tutorial',
             'Guía paso a paso para consultar y descargar tesis del repositorio institucional desde cualquier dispositivo.', True),
            ('Manual del sistema de préstamos v2.1',                    'manual',
             'Documentación completa sobre el proceso de solicitud, renovación y devolución de libros en el sistema de biblioteca.', True),
            ('Webinar: Gestión documental en instituciones cubanas',     'video',
             'Grabación del webinar sobre mejores prácticas en gestión documental para instituciones de educación superior en Cuba.', False),
            ('Novedades en legislación urbanística 2024',               'novedad',
             'Resumen de las principales actualizaciones en la normativa de ordenamiento territorial y urbanismo vigente en Cuba.', True),
            ('Tutorial: Cómo realizar una búsqueda avanzada',           'tutorial',
             'Aprende a usar los filtros avanzados del portal para encontrar libros, tesis y recursos de forma eficiente.', True),
        ]

        for titulo, tipo, desc, destacado in recursos_data:
            Recurso.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'tipo':        tipo,
                    'descripcion': desc,
                    'publicado':   True,
                    'destacado':   destacado,
                    'autor':       admin_user,
                }
            )

        self.stdout.write('  Recursos creados.')

        self.stdout.write(self.style.SUCCESS(
            '\nDatos de prueba creados correctamente.\n'
            'Usuarios disponibles (contraseña: prueba1234):\n'
            '  bibliotecario1 — Bibliotecario (staff)\n'
            '  estudiante1    — Estudiante\n'
            '  estudiante2    — Estudiante\n'
            '  estudiante3    — Estudiante\n'
            '  profesor1      — Profesor\n'
            '  visitante1     — Visitante\n'
        ))