from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from kepi.bowler_pub.create import create
import kepi.bowler_pub.crypto as crypto
from kepi.bowler_pub.utils import uri_to_url
from django.utils.timezone import now
from django.core.exceptions import ValidationError
import logging

logger = logging.Logger('kepi')

class Notification(models.Model):

    FOLLOW = 'F'
    MENTION = 'M'
    REBLOG = 'R'
    FAVOURITE = 'L'

    TYPE_CHOICES = [
            (FOLLOW, 'follow'),
            (MENTION, 'mention'),
            (REBLOG, 'reblog'),
            (FAVOURITE, 'favourite'),
            ]

    notification_type = models.CharField(
            max_length = 1,
            choices = TYPE_CHOICES,
            )

    created_at = models.DateTimeField(
            default = now,
            )

    for_account = models.ForeignKey(
            'Person',
            on_delete = models.DO_NOTHING,
            related_name = 'notifications_for',
            )

    about_account = models.ForeignKey(
            'Person',
            on_delete = models.DO_NOTHING,
            related_name = 'notifications_about',
            blank = True,
            null = True,
            )

    status = models.ForeignKey(
            'Status',
            on_delete = models.DO_NOTHING,
            blank = True,
            null = True,
            )

    def __str__(self):

        if self.notification_type == self.FOLLOW:
            detail = '%s has followed you' % (self.about_account,)
        elif self.notification_type == self.MENTION:
            detail = '%s has mentioned you' % (self.about_account,)
        elif self.notification_type == self.REBLOG:
            detail = '%s has reblogged you' % (self.about_account,)
        elif self.notification_type == self.FAVOURITE:
            detail = '%s has favourited your status' % (self.about_account,)
        else:
            detail = '(%s?)' % (self.notification_type,)

        return '[%s: %s]' % (
                self.for_account.id,
                detail,
                )