from django.core.management.base import BaseCommand
from biblioteca.correo import procesar_notificaciones_pendientes


class Command(BaseCommand):
    help = 'Envía notificaciones de correo para préstamos vencidos y por vencer'

    def handle(self, *args, **options):
        self.stdout.write('Procesando notificaciones...')
        enviados = procesar_notificaciones_pendientes()
        self.stdout.write(
            self.style.SUCCESS(f'{enviados} notificación(es) enviada(s).')
        )