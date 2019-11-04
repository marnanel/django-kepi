# views/nodeinfo.py
#
# Part of chapeau, an ActivityPub daemon.
# Copyright (c) 2018-2019 Marnanel Thurman.
# Licensed under the GNU Public License v2.

"""
Implements nodeinfo.
See [http://nodeinfo.diaspora.software/protocol.html](Diaspora's site)
for the full details.
"""

import django.views
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from chapeau import __version__
import logging
import re
from chapeau.kepi.utils import as_json

logger = logging.Logger('chapeau')

class NodeinfoPart1(django.views.View):
    """
    Nodeinfo support.
    This part must appear at "/.well-known/nodeinfo".
    """

    def get(self, request):

        logger.info('Returning nodeinfo.')

        result = {
                "links": [
                    {
                        "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
                        "href": request.build_absolute_uri("/nodeinfo.json"),
                        },
                    ],
                }

        return HttpResponse(
                status = 200,
                reason = 'Here you go',
                content = bytes(as_json(result),
                    encoding='utf-8'),
                content_type='application/json; '+\
                        'profile=http://nodeinfo.diaspora.software/ns/schema/2.0#')

class NodeinfoPart2(django.views.View):
    """
    Nodeinfo support.

    This should be at "/nodeinfo.json".
    """

    def _get_body(self, request):

        result = {
                "version": "2.0",
                "software" : {
                    "name": "chapeau",
                    "version": __version__,
                },
                "protocols": ['activitypub'],
                "services": {
                    "inbound": [],
                    "outbound": [],
                    },
                "openRegistrations": False,
                "usage": {
                    "users": {
                        # When this information is meaningful,
                        # we can implement this more seriously.
                        "total": 1,
                        "activeMonth": 1,
                        },
                    "localPosts": 0,
                    "localComments": 0,
                    },
                "metadata": {
                    },
                }

        return HttpResponse(
                status = 200,
                reason = 'Here you go',
                content = bytes(as_json(result),
                    encoding='utf-8'),
                content_type='application/json; '+\
                        'profile=http://nodeinfo.diaspora.software/ns/schema/2.0#')

    def get(self, request):
        result = self._get_body(request)

        result['Access-Control-Allow-Origin'] = '*'
        return result
