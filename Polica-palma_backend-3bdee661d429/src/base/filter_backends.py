import datetime
# from datetime import datetime


from django.db import models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils.dateparse import parse_datetime
from rest_framework.compat import coreapi, coreschema
from django_filters import rest_framework as django_filters

from src.core.helpers import try_parsing_date


class CustomFilterBackend(DjangoFilterBackend):
    raise_exception = False


class CustomDateRangeFilter(filters.BaseFilterBackend):
    """
    Filter queryset based on a date range defined by 'start_date' and 'end_date' query parameters.
    """

    DATE_FORMAT = '%d.%m.%Y'

    def parse_datetime(self, date_string):
        return try_parsing_date(date_string)

    def get_start_date_filter(self, date_field, start_date):
        return {f"{date_field}__gte": start_date}

    def get_end_date_filter(self, date_field, end_date):
        return {f"{date_field}__lte": end_date}

    def filter_queryset(self, request, queryset, view):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        date_fields = getattr(view, 'filter_date_field', None)
        date_filter_ignore_actions = getattr(view, 'date_filter_ignore_actions', None)

        if view.action in date_filter_ignore_actions:
            return queryset

        if not date_fields:
            raise Exception("Improperly configured view")

        for date_field in date_fields:
            if not isinstance(date_field, str):
                raise Exception("Improperly configured view")

            if not start_date or start_date == "":
                # start_date = timezone.now().replace(hour=0, minute=0, second=0)
                start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0,
                                                    tzinfo=timezone.get_current_timezone())
                # start_date = datetime.datetime.now().replace(
                #     hour=0, minute=0, second=0)
                queryset = queryset.filter(**self.get_start_date_filter(date_field, start_date))
            if not end_date or end_date == "":
                end_date = timezone.now()
                queryset = queryset.filter(**self.get_end_date_filter(date_field, end_date))

            if isinstance(start_date, str) and len(start_date) > 0 and isinstance(end_date, str) and len(end_date) > 0:
                start_date = self.parse_datetime(start_date)
                end_date = self.parse_datetime(end_date).replace(hour=23, minute=59, second=59)

                return queryset.filter(
                    models.Q(**self.get_start_date_filter(date_field, start_date)) &
                    models.Q(**self.get_end_date_filter(date_field, end_date))
                )
            if isinstance(start_date, str) and len(start_date) > 0:
                start_date = self.parse_datetime(start_date)
                return queryset.filter(**self.get_start_date_filter(date_field, start_date))
            if isinstance(end_date, str) and len(end_date) > 0:
                end_date = self.parse_datetime(end_date).replace(hour=23, minute=59, second=59)

                return queryset.filter(**self.get_end_date_filter(date_field, end_date))

        return queryset

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        fields = [
            coreapi.Field(
                name='start_date',
                required=False,
                location='query',
                schema=coreschema.String(
                    title="Start Date",
                    description="Start date in DD.MM.YYYY format"
                ),
            ),
            coreapi.Field(
                name='end_date',
                required=False,
                location='query',
                schema=coreschema.String(
                    title="End Date",
                    description="End date in DD.MM.YYYY format"
                ),
            ),
        ]
        return fields

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': 'start_date',
                'required': False,
                'in': 'query',
                'description': "Start date in DD.MM.YYYY format",
                'schema': {
                    'type': 'string',
                },
            },
            {
                'name': 'end_date',
                'required': False,
                'in': 'query',
                'description': "End date in DD.MM.YYYY format",
                'schema': {
                    'type': 'string',
                },
            },
        ]


class CustomDateTimeRangeFilter(CustomDateRangeFilter):
    DATE_FORMAT = '%d.%m.%Y %H:%M'

    def filter_queryset(self, request, queryset, view):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        date_fields = getattr(view, 'filter_date_field', None)
        date_filter_ignore_actions = getattr(view, 'date_filter_ignore_actions', None)

        if view.action in date_filter_ignore_actions:
            return queryset

        if not date_fields:
            raise Exception("Improperly configured view")

        for date_field in date_fields:
            if not isinstance(date_field, str):
                raise Exception("Improperly configured view")

            if not start_date or start_date == "":
                # start_date = timezone.now().replace(hour=0, minute=0, second=0)
                start_date = timezone.now().replace(hour=0, minute=0, second=0, tzinfo=timezone.get_current_timezone())
                queryset = queryset.filter(**self.get_start_date_filter(date_field, start_date))
            if not end_date or end_date == "":
                end_date = timezone.now()
                queryset = queryset.filter(**self.get_end_date_filter(date_field, end_date))

            if isinstance(start_date, str) and len(start_date) > 0 and isinstance(end_date, str) and len(end_date) > 0:
                start_date = self.parse_datetime(start_date)
                end_date = self.parse_datetime(end_date)

                return queryset.filter(
                    models.Q(**self.get_start_date_filter(date_field, start_date)) &
                    models.Q(**self.get_end_date_filter(date_field, end_date))
                )
            if isinstance(start_date, str) and len(start_date) > 0:
                start_date = self.parse_datetime(start_date)
                return queryset.filter(**self.get_start_date_filter(date_field, start_date))
            if isinstance(end_date, str) and len(end_date) > 0:
                end_date = self.parse_datetime(end_date)

                return queryset.filter(**self.get_end_date_filter(date_field, end_date))

        return queryset

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        fields = [
            coreapi.Field(
                name='start_date',
                required=False,
                location='query',
                schema=coreschema.String(
                    title="Start Date",
                    description="Start date in DD.MM.YYYY HH:MM format"
                ),
            ),
            coreapi.Field(
                name='end_date',
                required=False,
                location='query',
                schema=coreschema.String(
                    title="End Date",
                    description="End date in DD.MM.YYYY HH:MM format"
                ),
            ),
        ]
        return fields

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': 'start_date',
                'required': False,
                'in': 'query',
                'description': "Start date in DD.MM.YYYY HH:MM format",
                'schema': {
                    'type': 'string',
                },
            },
            {
                'name': 'end_date',
                'required': False,
                'in': 'query',
                'description': "End date in DD.MM.YYYY HH:MM format",
                'schema': {
                    'type': 'string',
                },
            },
        ]