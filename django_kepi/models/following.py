from django.db import models
import logging

logger = logging.getLogger(name='django_kepi')

class Following(models.Model):

    follower = models.URLField(
            max_length=255,
            )

    following = models.URLField(
            max_length=255,
            )

    pending = models.BooleanField(
            default=True,
            )

    def __str__(self):

        if self.pending:
            pending = ' (pending acceptance)'
        else:
            pending = ''

        result = '[%s follows %s%s]' % (
                self.follower,
                self.following,
                pending,
                )
        return result

def _get_follow(follower, following):
    try:
        return Following.objects.get(follower=follower, following=following)
    except Following.DoesNotExist:
        return None

def request(follower, following):

    f = _get_follow(follower, following)

    if f is not None:

        logger.warn('follow request failed; %s already exists',
            f)

        if f.pending:
            raise ValueError('%s has already requested to follow %s',
                    follower, following)
        else:
            raise ValueError('%s is already following %s',
                    follower, following)

    result = Following(
            follower = follower,
            following = following,
            pending = True,
            )
    result.save()

    logger.info('%s has requested to follow %s',
            follower, following)

def accept(follower, following):

    result = _get_follow(follower, following)

    if result is None:

        logger.warn('accepting follow request that we didn\'t know about')

        result = Following(
                follower = follower,
                following = following,
                pending = False,
                )
    else:
        result.pending = False

    result.save()

    logger.info('%s has started to follow %s: %s',
            follower, following, result)

    return result

def reject(follower, following):

    f = _get_follow(follower, following)

    if f is None:
        logger.warn('rejecting follow request; '+
            'that\'s fine because we didn\'t know about it')
    else:
        f.delete()

    logger.info('%s was rejected as a follower of %s',
            follower, following)


