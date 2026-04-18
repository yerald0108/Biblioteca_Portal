from django.core.management.base import BaseCommand
from biblioteca.correo import procesar_notificaciones_pendientes
from biblioteca.models import Prestamo


class Command(BaseCommand):
    help = 'Actualiza estados vencidos y envía notificaciones de correo'

    def handle(self, *args, **options):
        # Primero actualizar todos los préstamos vencidos
        self.stdout.write('Actualizando préstamos vencidos...')
        actualizados = Prestamo.actualizar_vencidos()
        self.stdout.write(f'  {actualizados} préstamo(s) marcado(s) como vencido.')

        # Luego enviar notificaciones
        self.stdout.write('Procesando notificaciones...')
        enviados = procesar_notificaciones_pendientes()
        self.stdout.write(
            self.style.SUCCESS(f'  {enviados} notificación(es) enviada(s).')
        )