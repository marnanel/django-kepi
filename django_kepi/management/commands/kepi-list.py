from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django_kepi.models import *
from django_kepi.create import create
from django_kepi.management import KepiCommand
import os
import logging

logger = logging.Logger('django_kepi')

class Command(KepiCommand):

    help = 'list objects'

    def add_arguments(self, parser):

        super().add_arguments(parser)

        parser.add_argument('--all',
                help='show cached remote objects as well',
                action='store_true',
                )

    def handle(self, *args, **options):

        super().handle(*args, **options)

        if options['all']:
            results = AcObject.objects.all()
        else:
            results = AcObject.objects.filter_local_only()

        if not results.exists():
            self.stdout.write(
                    self.style.ERROR(
                        "Nothing found."
                        ))
            return

        for obj in results:
            self.stdout.write(' - %s' % (obj,))


