from django.urls import path
from . import views

app_name = 'biblioteca'

urlpatterns = [
    # Libros
    path('libros/',                           views.libro_list,         name='libro_list'),
    path('libros/nuevo/',                     views.libro_crear,        name='libro_crear'),
    path('libros/<int:pk>/',                  views.libro_detail,       name='libro_detail'),
    path('libros/<int:pk>/editar/',           views.libro_editar,       name='libro_editar'),
    path('libros/<int:pk>/eliminar/',         views.libro_eliminar,     name='libro_eliminar'),
    path('libros/<int:libro_pk>/ejemplar/',   views.ejemplar_agregar,   name='ejemplar_agregar'),

    # Préstamos
    path('prestamos/',                        views.prestamo_list,      name='prestamo_list'),
    path('prestamos/nuevo/',                  views.prestamo_crear,     name='prestamo_crear'),
    path('prestamos/<int:pk>/devolver/',      views.prestamo_devolver,  name='prestamo_devolver'),
    path('prestamos/<int:pk>/notificar/',     views.prestamo_notificar, name='prestamo_notificar'),
    
    # Tesis
    path('tesis/',                            views.tesis_list,         name='tesis_list'),
    path('tesis/nueva/',                      views.tesis_crear,        name='tesis_crear'),
    path('tesis/<int:pk>/',                   views.tesis_detail,       name='tesis_detail'),
    path('tesis/<int:pk>/editar/',            views.tesis_editar,       name='tesis_editar'),
    path('tesis/<int:pk>/eliminar/',          views.tesis_eliminar,     name='tesis_eliminar'),
    path('tesis/<int:pk>/pdf/',               views.tesis_ver_pdf,      name='tesis_ver_pdf'),
    
    # Profesores
    path('profesores/',                       views.profesor_list,      name='profesor_list'),
    path('profesores/nuevo/',                 views.profesor_crear,     name='profesor_crear'),
    path('profesores/<int:pk>/',              views.profesor_detail,    name='profesor_detail'),
    path('profesores/<int:pk>/editar/',       views.profesor_editar,    name='profesor_editar'),
    path('profesores/<int:pk>/eliminar/',     views.profesor_eliminar,  name='profesor_eliminar'),
    
    # Recursos / Novedades
    path('recursos/',                         views.recurso_list,       name='recurso_list'),
    path('recursos/nuevo/',                   views.recurso_crear,      name='recurso_crear'),
    path('recursos/<int:pk>/',                views.recurso_detail,     name='recurso_detail'),
    path('recursos/<int:pk>/editar/',         views.recurso_editar,     name='recurso_editar'),
    path('recursos/<int:pk>/eliminar/',       views.recurso_eliminar,   name='recurso_eliminar'),
    path('recursos/<int:pk>/descargar/',      views.recurso_descargar,  name='recurso_descargar'),
    
    # Panel y perfiles
    path('panel/',                            views.panel_bibliotecario, name='panel'),
    path('mi-perfil/',                        views.mi_perfil,           name='mi_perfil'),
    path('usuarios/',                         views.usuario_list,        name='usuario_list'),
    path('usuarios/<int:pk>/editar/',         views.usuario_editar,      name='usuario_editar'),
    
    path('notificaciones/', views.notificaciones_list, name='notificaciones'),
    
    # Solicitudes de préstamo
    path('solicitudes/',                        views.solicitud_list,    name='solicitud_list'),
    path('solicitudes/mis/',                    views.mis_solicitudes,   name='mis_solicitudes'),
    path('solicitudes/<int:pk>/aprobar/',       views.solicitud_aprobar, name='solicitud_aprobar'),
    path('solicitudes/<int:pk>/rechazar/',      views.solicitud_rechazar,name='solicitud_rechazar'),
    path('libros/<int:libro_pk>/solicitar/',    views.solicitud_crear,   name='solicitud_crear'),
]