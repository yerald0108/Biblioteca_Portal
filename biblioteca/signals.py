from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import PerfilUsuario


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        rol = 'bibliotecario' if instance.is_staff else 'visitante'
        PerfilUsuario.objects.create(
            usuario=instance,
            rol=rol,
            rol_aprobado=instance.is_staff
        )


@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()