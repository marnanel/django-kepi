from django.test import TestCase
from unittest import skip
from chapeau.kepi.create import create
from chapeau.kepi.models import *
import logging

logger = logging.getLogger(name='chapeau')

class TestPolymorph(TestCase):

    def test_invalid_type(self):
        t = create(
                f_type = 'Wombat',
                )
        self.assertIsNone(t)

    def test_note(self):
        t = create(
                f_type = 'Note',
                )
        self.assertIsInstance(t, AcItem)

    def test_person(self):
        t = create(
                f_type = 'Person',
                id = '@wombat',
                )
        self.assertIsInstance(t, AcActor)

    @skip('Are Object etc really abstract?')
    def test_abstract(self):
        t = create(
                f_type = 'Object',
                )
        self.assertIsNone(t)
