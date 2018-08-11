from django.shortcuts import render, get_object_or_404
import django.views
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
import json
import re
from django_kepi.models import ActivityObject

def render(data):
    # XXX merge in
    result = JsonResponse(
            data=data,
            json_dumps_params={
                'sort_keys': True,
                'indent': 2,
                }
            )

    result['Content-Type'] = 'application/activity+json'

    return result

class ActivityObjectView(django.views.View):

    def get(self, request, *args, **kwargs):

        instance = ActivityObject.objects.get(pk=kwargs['id'])

        result = instance.activity_fields()

        return render(result)
