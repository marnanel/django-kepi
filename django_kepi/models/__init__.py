from django_kepi.models.thing import Thing, ThingField, create
from django_kepi.models.following import Following

def new_activity_identifier():
    # we have to keep this in for now,
    # to pacify makemigrations
    return None

#######################

__all__ = [
        'Thing',
        'ThingField',
        'create',
        'Following',
        'new_activity_identifier',
        ]