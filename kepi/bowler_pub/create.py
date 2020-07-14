# create.py
#
# Part of kepi.
# Copyright (c) 2018-2020 Marnanel Thurman.
# Licensed under the GNU Public License v2.

"""
This contains create(), which creates the appropriate
model instance when we've received an ActivityPub message.

create() is called by validate() when we've validated
the message.
"""

import logging
import kepi.trilby_api.models as trilby_models
import kepi.trilby_api.utils as trilby_utils
import kepi.bowler_pub.utils as bowler_utils

logger = logging.getLogger(name='kepi')

def create(message):

    fields = message.fields
    logger.debug('%s: creating from %s',
            message, message.fields)

    if '_' in fields['type']:
        # no types have underscores in their names, and
        # in this module we use the underscore to separate
        # activity type names from object type names

        logger.warn('%s: underscore in type name "%s"; looks dodgy',
                message,
                fields['type'],
                )
        return

    activity_handler_name = 'on_%s' % (
            fields['type'].lower(),
            )

    object_handler_name = None

    try:
        object_handler_name = '%s_%s' % (
                activity_handler_name,
                fields['object']['type'].lower(),
                )
    except KeyError:
        pass
    except ValueError:
        pass

    if object_handler_name in globals():
        result = globals()[object_handler_name](message)
        return result

    if activity_handler_name in globals():
        result = globals()[activity_handler_name](message)
        return result

    if object_handler_name is not None:
        logger.warn('%s: no handler for %s or %s',
                message,
                activity_handler_name,
                object_handler_name)
    else:
        logger.warn('%s: no handler for %s',
                message,
                activity_handler_name)

def on_follow(message):

    fields = message.fields
    logger.debug('%s: on_follow %s', message, fields)

    follower = trilby_models.Person.lookup(fields['actor'],
            create_missing_remote = True)

    if follower is None:
        # shouldn't happen
        logger.warn('%s: could not find remote user %s',
                message,
                fields['actor'],
                )
        return

    following = trilby_models.Person.lookup(fields['object'])
    if following is None:
        logger.info('%s: there is no local user %s',
                message,
                fields['object'],
                )
        return

    result = trilby_models.Follow(
            follower = follower,
            following = following,
            )

    result.save()
    return result

def _visibility_from_fields(fields):

    def get_list(fields, fieldname):
        result = fields.get(fieldname, [])
        if not isinstance(result, list):
            result = [result]
        return result

    audience = dict([
        (fieldname, get_list(fields, fieldname))
        for fieldname in ['to', 'cc']
        ])

    for group, result in [
            ('to', trilby_utils.VISIBILITY_PUBLIC),
            ('cc', trilby_utils.VISIBILITY_UNLISTED),
            ]:
        for someone in audience[group]:
            if someone in PUBLIC:
                return result

    # default
    return trilby_utils.VISIBILITY_DIRECT

def on_create_note(message):
    fields = message.fields
    logger.debug('%s: on_create_note %s', message, fields)

    newborn_fields = fields['object']

    poster = trilby_models.Person.lookup(
        name = fields['actor'],
        create_missing_remote = True,
        )

    if 'inReplyTo' in newborn_fields:
        in_reply_to = trilby_models.Status.lookup(
            url = newborn_fields['inReplyTo'],
            )
    else:
        in_reply_to = None

    is_sensitive = False # FIXME
    spoiler_text = '' # FIXME
    language = 'en' # FIXME

    visibility = _visibility_from_fields(fields)

    newbie = trilby_models.Status(
        remote_url = fields['id'],
        account = poster,
        in_reply_to = in_reply_to,
        content = newborn_fields['content'],
        sensitive = is_sensitive,
        spoiler_text = spoiler_text,
        visibility = visibility,
        language = language,
            )

    newbie.save()

    logger.debug('%s: created status %s',
        message,
        newbie,
        )
