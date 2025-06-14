import re

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden

from PalmaCrm import settings
from src.user.models import ViewPermissionRule


class PermissionControlMiddleware(object):

    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.get_response = get_response

        self.required = tuple(re.compile(url)
                              for url in settings.LOGIN_REQUIRED_URLS)
        self.exceptions = tuple(re.compile(url)
                                for url in settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None
        elif request.user.is_superuser:
            return None
        user_permissions = ViewPermissionRule.objects.select_related('permission') \
            .exclude(Q(users__user=request.user) |
                     Q(viewpermissionrulegroup__users__user=request.user))
        permissions_list = user_permissions.values_list('permission__path_name', flat=True)
        # No need to process URLs if user already logged in
        if request.resolver_match.url_name in permissions_list:
            return HttpResponseForbidden("403 Forbidden , you don't have access")
        else:
            return None


class RequireLoginMiddleware(object):

    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.get_response = get_response

        self.required = tuple(re.compile(url)
                              for url in settings.LOGIN_REQUIRED_URLS)
        self.exceptions = tuple(re.compile(url)
                                for url in settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)

    def __call__(self, request):

        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        # No need to process URLs if user already logged in
        if request.user.is_authenticated:
            return None

        # An exception match should immediately return None
        for url in self.exceptions:
            if url.match(request.path):
                return None

        # Requests matching a restricted URL pattern are returned
        # wrapped with the login_required decorator
        for url in self.required:
            if url.match(request.path):
                return login_required(view_func)(request, *view_args, **view_kwargs)

        # Explicitly return None for all non-matching requests
        return None