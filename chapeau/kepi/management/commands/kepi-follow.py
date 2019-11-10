from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from chapeau.kepi.models import *
from chapeau.kepi.create import create
from chapeau.kepi.management import KepiCommand
import os
import logging

logger = logging.Logger('chapeau')

class Command(KepiCommand):

    help = 'follow a user'

    def add_arguments(self, parser):

        super().add_arguments(parser)

        parser.add_argument('whom',
                help='account to follow',
                )

    def handle(self, *args, **options):

        super().handle(*args, **options)

        obj = create(value={
            'type': 'Follow',
            'actor': self._actor,
            'to': options['whom'],
            'object': options['whom'],
            },
            is_local_user=True,
            )
        logger.info('Follow created: %s', obj)
