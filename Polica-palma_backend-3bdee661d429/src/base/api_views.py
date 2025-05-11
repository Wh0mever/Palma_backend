from collections import OrderedDict

from rest_framework import viewsets, pagination
from rest_framework.response import Response
from rest_framework.compat import coreapi, coreschema


class MultiSerializerViewSetMixin:
    """
    Mixin that allows use different serializer for different actions
    """
    serializer_action_classes = {}

    def get_serializer_class(self):
        serializer = self.serializer_action_classes.get(self.action)
        if not serializer:
            serializer = super().get_serializer_class()
        return serializer


class DynamicDepthViewSet(viewsets.ModelViewSet):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        depth = 0
        try:
            depth = int(self.request.query_params.get('depth', 0))
        except ValueError:
            pass  # Ignore non-numeric parameters and keep default 0 depth

        context['depth'] = depth

        return context


class DestroyFlagsViewSetMixin:
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        return Response(status=204)


class PermissionPolicyMixin:
    def check_permissions(self, request):
        try:
            # This line is heavily inspired from `APIView.dispatch`.
            # It returns the method associated with an endpoint.
            handler = getattr(self, request.method.lower())
        except AttributeError:
            handler = None

        if (
                handler
                and self.permission_classes_per_method
                and self.permission_classes_per_method.get(handler.__name__)
        ):
            self.permission_classes = self.permission_classes_per_method.get(handler.__name__)

        super().check_permissions(request)


class CustomPagination(pagination.PageNumberPagination):
    page_size = 20

    def paginate_queryset(self, queryset, request, view=None):
        paginate = bool(request.query_params.get('page', None))
        if paginate:
            return super().paginate_queryset(queryset, request, view)
        return None

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class AnalyticsTablePagination(pagination.PageNumberPagination):
    page_size = 10

    def paginate_queryset(self, queryset, request, view=None):
        paginate = bool(request.query_params.get('page', None))
        if paginate:
            return super().paginate_queryset(queryset, request, view)
        return None

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
