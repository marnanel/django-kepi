from django.test import TestCase, Client
from django_kepi.validation import IncomingMessage, validate
from django_kepi.models import Thing
from unittest import skip
from unittest.mock import Mock, patch
from . import _create_person
import logging
import httpsig
import json

# FIXME test caching
# FIXME test invalid keys

logger = logging.getLogger(name='django_kepi')

ACTIVITY_ID = "https://example.com/04b065f8-81c4-408e-bec3-9fb1f7c06408"
INBOX_HOST = 'europa.example.com'
INBOX_PATH = '/inbox'

REMOTE_FRED = 'https://remote.example.org/users/fred'
REMOTE_JIM = 'https://remote.example.org/users/jim'

FREDS_INBOX = REMOTE_FRED+'/inbox'
JIMS_INBOX = REMOTE_JIM+'/inbox'
REMOTE_SHARED_INBOX = 'https://remote.example.org/shared-inbox'

LOCAL_ALICE = 'https://altair.example.com/users/alice'
LOCAL_BOB = 'https://altair.example.com/users/bob'

MESSAGE_CONTEXT = ["https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {"manuallyApprovesFollowers":"as:manuallyApprovesFollowers",
            "sensitive":"as:sensitive",
            "movedTo":{"@id":"as:movedTo",
                "@type":"@id"},
            "alsoKnownAs":{"@id":"as:alsoKnownAs",
                "@type":"@id"},
            "Hashtag":"as:Hashtag",
            "ostatus":"http://ostatus.org#",
            "atomUri":"ostatus:atomUri",
            "inReplyToAtomUri":"ostatus:inReplyToAtomUri",
            "conversation":"ostatus:conversation",
            "toot":"http://joinmastodon.org/ns#",
            "Emoji":"toot:Emoji",
            "focalPoint":{"@container":"@list",
                "@id":"toot:focalPoint"},
            "featured":{"@id":"toot:featured",
                "@type":"@id"},
            "schema":"http://schema.org#",
            "PropertyValue":"schema:PropertyValue",
            "value":"schema:value"}]

def _test_message(secret='', **fields):

    body = dict([(f[2:],v) for f,v in fields.items() if f.startswith('f_')])
    body['@context'] = MESSAGE_CONTEXT
    body['Host'] = INBOX_HOST

    headers = {
            'content-type': "application/activity+json",
            'date': "Thu, 04 Apr 2019 21:12:11 GMT",
            'host': INBOX_HOST,
            }

    if 'key_id' in fields:
        key_id = fields['key_id']
    else:
        key_id = body['actor']+'#main-key'

    signer = httpsig.HeaderSigner(
            secret=secret,
            algorithm='rsa-sha256',
            key_id = key_id,
            headers=['(request-target)', 'host', 'date', 'content-type'],
            )

    headers = signer.sign(
            headers,
            method='POST',
            path=INBOX_PATH,
            )

    SIGNATURE = 'Signature'
    if headers['Authorization'].startswith(SIGNATURE):
        headers['Signature'] = headers['Authorization'][len(SIGNATURE)+1:]

    result = IncomingMessage(
            content_type = headers['content-type'],
            date = headers['date'],
            digest = '', # FIXME ???
            host = headers['host'],
            path = INBOX_PATH,
            signature = headers['Signature'],
            body = json.dumps(body, sort_keys=True),
            )

    result.save()
    return result

def _remote_user(url, name,
        publicKey='',
        inbox=None,
        sharedInbox=None,
        ):
        result = {
                '@context': MESSAGE_CONTEXT,
                'id': url,
                'type': 'Person',
                'following': '',
                'followers': '',
                'outbox': '',
                'featured': '',
                'preferredUsername': name,
                'url': url,
                'publicKey': {
                    'id': url+'#main-key',
                    'owner': url,
                    'publicKeyPem': publicKey,
                    },
                }

        if inbox is not None:
            result['inbox'] = inbox

        if sharedInbox is not None:
            result['endpoints'] = {
                    'sharedInbox': sharedInbox,
                    }


        return result

def _message_became_activity(url=ACTIVITY_ID):
    try:
        result = Thing.objects.get(remote_url=url)
        return True
    except Thing.DoesNotExist:
        return False

class ResultWrapper(object):
    def __init__(self,
            text='',
            status_code=200,
            ):
        self.text = json.dumps(text)
        self.status_code = status_code

class TestValidationTasks(TestCase):

    @skip("Requires lookup of local actors' private keys, which requires delegate lookup")
    @patch('requests.get')
    def test_local_lookup(self, mock_get):
        keys = json.load(open('tests/keys/keys-0000.json', 'r'))

        alice = _create_person(
                name = 'alice',
                publicKey = keys['public'],
                )
        alice.save()
        logger.debug('%s', alice.url)

        message = _test_message(
                f_id=ACTIVITY_ID,
                f_type="Follow",
                f_actor=LOCAL_ALICE,
                f_object=LOCAL_BOB,
                secret = keys['private'],
                )

        validate(message.id)

        self.assertTrue(_message_became_activity())
        mock_get.assert_not_called()

    @patch('requests.get')
    def test_remote_user_known(self, mock_get):

        keys = json.load(open('tests/keys/keys-0001.json', 'r'))
        mock_get.return_value = ResultWrapper(
                text = _remote_user(
                    url = REMOTE_FRED,
                    name = 'Fred',
                    # XXX This fails because publicKey is ordinarily a dict
                    # containing the string, not just a string
                    publicKey=keys['public']),
                )

        message = _test_message(
                f_id=ACTIVITY_ID,
                f_type="Follow",
                f_actor=REMOTE_FRED,
                f_object=LOCAL_ALICE,
                secret = keys['private'],
                )
        validate(message.id)

        self.assertTrue(_message_became_activity())
        mock_get.assert_called_once_with(REMOTE_FRED)

    @patch('requests.get')
    def test_remote_user_spoofed(self, mock_get):
        keys1 = json.load(open('tests/keys/keys-0001.json', 'r'))
        keys2 = json.load(open('tests/keys/keys-0002.json', 'r'))
        mock_get.return_value = ResultWrapper(
                text = _remote_user(
                    url = REMOTE_FRED,
                    name = 'Fred',
                    publicKey=keys2['public'],
                ))

        message = _test_message(
                f_id=ACTIVITY_ID,
                f_type="Follow",
                f_actor=REMOTE_FRED,
                f_object=LOCAL_ALICE,
                secret = keys1['private'],
                )
        validate(message.id)

        self.assertFalse(_message_became_activity())

        mock_get.assert_called_once_with(REMOTE_FRED)

    @patch('requests.get')
    def test_remote_user_gone(self, mock_get):
        keys = json.load(open('tests/keys/keys-0001.json', 'r'))
        mock_get.return_value = ResultWrapper(
                status_code = 410,
                )

        message = _test_message(
                f_id=ACTIVITY_ID,
                f_type="Follow",
                f_actor=REMOTE_FRED,
                f_object=LOCAL_ALICE,
                secret = keys['private'],
                )
        validate(message.id)

        self.assertFalse(_message_became_activity())

        mock_get.assert_called_once_with(REMOTE_FRED)

    @patch('requests.get')
    def test_remote_user_unknown(self, mock_get):
        keys = json.load(open('tests/keys/keys-0001.json', 'r'))
        mock_get.return_value = ResultWrapper(
                status_code = 404,
                )

        message = _test_message(
                f_id=ACTIVITY_ID,
                f_type="Follow",
                f_actor=REMOTE_FRED,
                f_object=LOCAL_ALICE,
                secret = keys['private'],
                )
        validate(message.id)

        self.assertFalse(_message_became_activity())

        mock_get.assert_called_once_with(REMOTE_FRED)
