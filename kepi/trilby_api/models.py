from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
import kepi.bowler_pub.models as kepi_models
import kepi.bowler_pub.signals as kepi_signals
import kepi.bowler_pub.find as kepi_find
from django.utils.timezone import now
import logging

logger = logging.Logger('kepi')

class TrilbyUser(AbstractUser):

    actor = models.OneToOneField(
            kepi_models.AcPerson,
            on_delete=models.CASCADE,
            unique=True,
            default=None,
            )

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
            max_length = 256,
            choices = TYPE_CHOICES,
            )

    created_at = models.DateTimeField(
            default = now,
            )

    for_account = models.ForeignKey(
            TrilbyUser,
            on_delete = models.DO_NOTHING,
            )

    about_account = models.CharField(
            max_length = 256,
            default='',
            )

    status = models.ForeignKey(
            kepi_models.AcItem,
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

@receiver(kepi_signals.created)
def on_follow(sender, **kwargs):

    value = kwargs['value']

    if isinstance(value, kepi_models.AcFollow):

        follower_acperson = kepi_find.find(
                value['object'],
                local_only = True,
                )

        if follower_acperson is None:
            logger.info('  -- not storing a notification, because '+\
                    'nobody\'s being followed')
            return

        try:
            follower = TrilbyUser.objects.get(actor=follower_acperson)
        except TrilbyUser.DoesNotExist:
            logger.info('  -- not storing a notification, because '+\
                    'we don\'t know the person being followed')
            return

        logger.info('  -- storing a notification about this follow')

        following = value['actor']

        notification = Notification(
                notification_type = Notification.FOLLOW,
                for_account = follower,
                about_account = following,
                )

        notification.save()

        logger.info('      -- notification is: %s',
                notification)
