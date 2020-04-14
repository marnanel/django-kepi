from django.db import IntegrityError, transaction
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpResponse, JsonResponse
from oauth2_provider.models import Application
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import SuspiciousOperation
from django.conf import settings
import kepi.trilby_api.models as trilby_models
from .serializers import *
import kepi.trilby_api.signals as kepi_signals
from rest_framework import generics, response
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import kepi.trilby_api.receivers
import logging
import json
import re

logger = logging.Logger(name='kepi')

###########################

class Instance(View):

    def get(self, request, *args, **kwargs):

        result = {
            'uri': 'http://127.0.0.1',
            'title': settings.KEPI['INSTANCE_NAME'],
            'description': settings.KEPI['INSTANCE_DESCRIPTION'],
            'email': settings.KEPI['CONTACT_EMAIL'],
            'version': '1.0.0', # of the protocol
            'urls': {},
            'languages': settings.KEPI['LANGUAGES'],
            'contact_account': settings.KEPI['CONTACT_ACCOUNT'],
            }

        return JsonResponse(result)

###########################

def error_response(status, reason):
    return JsonResponse(
            {
                "error": reason,
                },
            status = status,
            reason = reason,
            )

###########################

class DoSomethingWithStatus(generics.GenericAPIView):

    serializer_class = StatusSerializer
    queryset = trilby_models.Status.objects.all()

    def _do_something_with(self, the_status, request):
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):

        if request.user is None:
            logger.debug('  -- user not logged in')
            return error_response(401, 'Not logged in')

        try:
            the_status = get_object_or_404(
                    self.get_queryset(),
                    id = int(kwargs['id']),
                    )
        except ValueError:
            return error_response(404, 'Non-decimal ID')

        self._do_something_with(the_status, request)

        serializer = StatusSerializer(
                the_status,
                context = {
                    'request': request,
                    },
                )

        return JsonResponse(
                serializer.data,
                status = 200,
                reason = 'Done',
                )

class Favourite(DoSomethingWithStatus):

    def _do_something_with(self, the_status, request):

        try:
            like = trilby_models.Like(
                liker = request.user.person,
                liked = the_status,
                )

            with transaction.atomic():
                like.save()

            logger.info('  -- created a Like')

            kepi_signals.liked.send(sender=like)

        except IntegrityError:
            logger.info('  -- not creating a Like; it already exists')

class Unfavourite(DoSomethingWithStatus):

    def _do_something_with(self, the_status, request):

        try:
            like = trilby_models.Like.objects.get(
                liker = request.user.person,
                liked = the_status,
                )

            logger.info('  -- deleting the Like: %s',
                    like)
            
            like.delete()

        except trilby_models.Like.DoesNotExist:
            logger.info('  -- not unliking; the Like doesn\'t exists')

###########################

class DoSomethingWithPerson(generics.GenericAPIView):

    serializer_class = UserSerializer
    queryset = trilby_models.Person.objects.all()

    def _do_something_with(self, the_person, request):
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):

        if request.user is None:
            logger.debug('  -- user not logged in')
            return error_response(401, 'Not logged in')

        the_person = get_object_or_404(
                self.get_queryset(),
                id = kwargs['name'],
                )

        self._do_something_with(the_person, request)

        serializer = UserSerializer(
                the_person,
                context = {
                    'request': request,
                    },
                )

        return JsonResponse(
                serializer.data,
                status = 200,
                reason = 'Done',
                )

class Follow(DoSomethingWithPerson):

    def _do_something_with(self, the_person, request):

        try:
            follow = trilby_models.Follow(
                follower = request.user.person,
                following = the_person,
                )

            with transaction.atomic():
                follow.save()

            logger.info('  -- follow: %s', follow)

            kepi_signals.followed.send(sender=follow)

        except IntegrityError:
            logger.info('  -- not creating a follow; it already exists')

###########################

def fix_oauth2_redirects():
    """
    Called from kepi.kepi.urls to fix a silly oversight
    in oauth2_provider. This isn't elegant.

    oauth2_provider.http.OAuth2ResponseRedirect checks the
    URL it's redirecting to, and raises DisallowedRedirect
    if it's not a recognised protocol. But this breaks apps
    like Tusky, which registers its own protocol with Android
    and then redirects to that in order to bring itself
    back once authentication's done.

    There's no way to fix this as a user of that package.
    Hence, we have to monkey-patch that class.
    """

    def fake_validate_redirect(not_self, redirect_to):
        return True

    from oauth2_provider.http import OAuth2ResponseRedirect as OA2RR
    OA2RR.validate_redirect = fake_validate_redirect
    logger.info("Monkey-patched %s.", OA2RR)

###########################

class Apps(View):

    def post(self, request, *args, **kwargs):

        new_app = Application(
            name = request.POST['client_name'],
            redirect_uris = request.POST['redirect_uris'],
            client_type = 'confidential',
            authorization_grant_type = 'authorization-code',
            user = None, # don't need to be logged in
            )

        new_app.save()

        result = {
            'id': new_app.id,
            'client_id': new_app.client_id,
            'client_secret': new_app.client_secret,
            }

        return JsonResponse(result)

class Verify_Credentials(generics.GenericAPIView):

    queryset = TrilbyUser.objects.all()

    def get(self, request, *args, **kwargs):
        serializer = UserSerializerWithSource(request.user.person)
        return JsonResponse(serializer.data)

class User(generics.GenericAPIView):

    queryset = trilby_models.Person.objects.all()

    def get(self, request, *args, **kwargs):
        whoever = get_object_or_404(
                self.get_queryset(),
                id='@'+kwargs['name'],
                )

        serializer = UserSerializer(whoever)
        return JsonResponse(serializer.data)

class Statuses(generics.ListCreateAPIView,
        generics.CreateAPIView,
        generics.DestroyAPIView,
        ):

    queryset = trilby_models.Status.objects.filter(remote_url=None)
    serializer_class = StatusSerializer

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        if 'id' in kwargs:
            number = kwargs['id']
            logger.info('Looking up status numbered %s, for %s',
                    number, request.user)

            try:
                activity = queryset.get(id=number)

                serializer = StatusSerializer(
                        activity,
                        partial = True,
                        context = {
                            'request': request,
                            },
                        )
            except Status.DoesNotExist:

                return error_response(
                        status = 404,
                        reason = 'Record not found',
                        )

        else:
            logger.info('Looking up all visible statuses, for %s',
                   request.user)

            serializer = StatusSerializer(
                    queryset,
                    context = {
                        'request': request,
                        },
                    many = True,
                    )

        return JsonResponse(serializer.data,
                safe = False, # it's a list
                )

    def _string_to_html(self, s):
        # FIXME this should be a bit more sophisticated :)
        return '<p>{}</p>'.format(s)

    def create(self, request, *args, **kwargs):

        data = request.data

        if 'status' not in data and 'media_ids' not in data:
            return HttpResponse(
                    status = 400,
                    content = 'You must supply a status or some media IDs',
                    )

        content = self._string_to_html(data.get('status'))

        status = trilby_models.Status(
                account = request.user.person,
                content = content,
                sensitive = data.get('sensitive', False),
                spoiler_text = data.get('spoiler_text', ''),
                visibility = data.get('visibility', 'public'),
                language = data.get('language',
                    settings.KEPI['LANGUAGES'][0]),
                # FIXME: in_reply_to
                # FIXME: media_ids
                # FIXME: idempotency_key
                )

        status.save()

        serializer = StatusSerializer(
                status,
                partial = True,
                context = {
                    'request': request,
                    },
                )

        return JsonResponse(
                serializer.data,
                status = 200, # should really be 201 but the spec says 200
                reason = 'Hot off the press',
                )

    def delete(self, request, *args, **kwargs):

        if 'id' not in kwargs:
            return error_response(404, 'Can\'t delete all statuses at once')

        the_status = get_object_or_404(
                self.get_queryset(),
                id = int(kwargs['id']),
                )

        if the_status.account != request.user.person:
            return error_response(404, # sic
                    'That isn\'t yours to delete')

        serializer = StatusSerializer(
                the_status,
                context = {
                    'request': request,
                    },
                )

        response = JsonResponse(serializer.data)

        the_status.delete()

        return response

class StatusContext(generics.ListCreateAPIView):

    queryset = trilby_models.Status.objects.all()

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        status = queryset.get(id=int(kwargs['id']))
        serializer = StatusContextSerializer(status)

        return JsonResponse(serializer.data)

class AbstractTimeline(generics.ListAPIView):

    serializer_class = StatusSerializer
    permission_classes = [
            IsAuthenticated,
            ]

    def get_queryset(self, request):
        raise NotImplementedError("cannot query abstract timeline")

    def get(self, request):
        queryset = self.get_queryset(request)
        serializer = self.serializer_class(queryset,
                many = True,
                context = {
                    'request': request,
                    })
        return Response(serializer.data)

PUBLIC_TIMELINE_SLICE_LENGTH = 20

class PublicTimeline(AbstractTimeline):

    permission_classes = ()

    def get_queryset(self, request):

        result = trilby_models.Status.objects.filter(
                visibility = Status.PUBLIC,
                )[:PUBLIC_TIMELINE_SLICE_LENGTH]

        return result

class HomeTimeline(AbstractTimeline):

    permission_classes = [
            IsAuthenticated,
            ]

    def get_queryset(self, request):

        return request.user.person.inbox

########################################

# TODO stub
class AccountsSearch(generics.ListAPIView):

    queryset = trilby_models.Person.objects.all()
    serializer_class = UserSerializer

    permission_classes = [
            IsAuthenticated,
            ]

########################################

# TODO stub
class Search(View):

    permission_classes = [
            IsAuthenticated,
            ]

    def get(self, request, *args, **kwargs):

        result = {
                'accounts': [],
                'statuses': [],
                'hashtags': [],
            }

        return JsonResponse(result)

########################################

class UserFeed(View):

    permission_classes = ()

    def get(self, request, username, *args, **kwargs):

        user = get_object_or_404(trilby_models.Person,
                id = '@'+username,
                )

        context = {
                'self': request.build_absolute_uri(),
                'user': user,
                'statuses': user.outbox,
                'server_name': settings.KEPI['LOCAL_OBJECT_HOSTNAME'],
            }

        result = render(
                request=request,
                template_name='account.atom.xml',
                context=context,
                content_type='application/atom+xml',
                )

        links = ', '.join(
                [ '<{}>; rel="{}"; type="{}"'.format(
                    settings.KEPI[uri].format(
                        hostname = settings.KEPI['LOCAL_OBJECT_HOSTNAME'],
                        username = user.id[1:],
                        ),
                    rel, mimetype)
                    for uri, rel, mimetype in
                    [
                        ('USER_WEBFINGER_URLS',
                            'lrdd',
                            'application/xrd+xml',
                            ),

                        ('USER_FEED_URLS',
                            'alternate',
                            'application/atom+xml',
                            ),

                        ('USER_FEED_URLS',
                            'alternate',
                            'application/activity+json',
                            ),
                        ]
                    ])

        result['Link'] = links

        return result

########################################

class Notifications(generics.ListAPIView):

    serializer_class = NotificationSerializer

    permission_classes = [
            IsAuthenticated,
            ]

    def list(self, request):
        queryset = Notification.objects.filter(
                for_account = request.user.person,
                )

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

########################################

class Emojis(View):
    # FIXME
    def get(self, request, *args, **kwargs):
        return JsonResponse([],
                safe=False)

class Filters(View):
    # FIXME
    def get(self, request, *args, **kwargs):
        return JsonResponse([],
                safe=False)

class Followers(View):
    # FIXME
    def get(self, request, *args, **kwargs):
        return JsonResponse([],
                safe=False)

class Following(View):
    # FIXME
    def get(self, request, *args, **kwargs):
        return JsonResponse([],
                safe=False)
