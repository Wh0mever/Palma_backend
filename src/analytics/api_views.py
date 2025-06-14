from datetime import datetime

from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from src.analytics.enums import ProductAnalyticsIndicator, FloristsAnalyticsIndicator, SalesmenAnalyticsIndicator, \
    OutlaysAnalyticsIndicator, ClientsAnalyticsIndicator
from src.analytics.serializers import ClientAnalyticClientSerializer
from src.analytics.services import ProfitAnalyticsService, IndustryProfitAnalyticService, \
    CashierIncomeAnalyticsService, IndustrySalesAnalyticsService, OverallTurnoverShareAnalyticsService, \
    ProductAnalyticsService, ProductFactorySalesAnalyticsService, FloristsAnalyticsService, SalesmenAnalyticsService, \
    OutlaysAnalyticService, WriteOffsAnalyticsService, ClientsAnalyticsService, ClientsTopAnalyticsService
from src.base.api_views import AnalyticsTablePagination
from src.product.models import Industry


class DateRangeFilterMixin:
    def get_start_end_dates(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if not start_date or start_date == "":
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0,
                                                tzinfo=timezone.get_current_timezone())
            # start_date = timezone.now().replace(month=5, tzinfo=timezone.get_current_timezone())
        if not end_date or end_date == "":
            end_date = timezone.now().replace(hour=23, minute=59, second=59, tzinfo=timezone.get_current_timezone())

        if isinstance(start_date, str) and len(start_date) > 0:
            start_date = timezone.make_aware(datetime.strptime(start_date, "%d.%m.%Y"))
        if isinstance(end_date, str) and len(end_date) > 0:
            end_date = timezone.make_aware(datetime.strptime(end_date, "%d.%m.%Y")).replace(
                hour=23, minute=59, second=59
            )

        return start_date, end_date


class ProfitAnalyticsView(DateRangeFilterMixin, APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get(self, request):
        start_date, end_date = self.get_start_end_dates()
        result = ProfitAnalyticsService(start_date, end_date).get_final_result_data()
        return Response(data=result)


class IndustryProfitAnalyticsView(DateRangeFilterMixin, APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        start_date, end_date = self.get_start_end_dates()
        industry_id = self.request.query_params.get('industry')
        industry = Industry.objects.get(pk=industry_id) if industry_id else None
        result = IndustryProfitAnalyticService(start_date, end_date, industry).get_final_result_data()
        return Response(data=result)


class CashierIncomeAnalyticsView(DateRangeFilterMixin, APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get(self, request):
        start_date, end_date = self.get_start_end_dates()
        result = CashierIncomeAnalyticsService(start_date, end_date).get_final_result_data()
        return Response(data=result)


class IndustryShareOfTurnoverAnalyticsView(DateRangeFilterMixin, ViewSet):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get_chart_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        result = IndustrySalesAnalyticsService(start_date, end_date).get_final_result_data()
        return Response(data=result)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get_table_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        result = IndustrySalesAnalyticsService(start_date, end_date).get_table_data()
        return Response(data=result)


class OverallTurnoverShareAnalyticsView(DateRangeFilterMixin, ViewSet):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get_chart_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        result = OverallTurnoverShareAnalyticsService(start_date, end_date).get_chart_data()
        return Response(data=result)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get_table_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        result = OverallTurnoverShareAnalyticsService(start_date, end_date).get_table_data()
        return Response(data=result)


class ProductsAnalyticsView(DateRangeFilterMixin, APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('indicator', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=ProductAnalyticsIndicator.values),
        ]
    )
    def get(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        indicator = self.request.query_params.get('indicator', ProductAnalyticsIndicator.TURNOVER_SUM)
        result = ProductAnalyticsService(indicator, start_date, end_date).get_final_result_data()
        return Response(data=result)


class ProductFactorySellsAnalyticsView(DateRangeFilterMixin, ViewSet):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get_chart_data(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        result = ProductFactorySalesAnalyticsService(start_date, end_date).get_final_result_data()
        return Response(data=result)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get_table_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        result = ProductFactorySalesAnalyticsService(start_date, end_date).get_table_data()
        return Response(data=result)


class FloristsAnalyticsView(DateRangeFilterMixin, APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('indicator', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=FloristsAnalyticsIndicator.values)
        ]
    )
    def get(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        indicator = self.request.query_params.get('indicator', FloristsAnalyticsIndicator.FINISHED_PRODUCTS)
        result = FloristsAnalyticsService(indicator, start_date, end_date).get_final_result_data()
        return Response(data=result)


class SalesmenAnalyticsView(DateRangeFilterMixin, APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('indicator', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=SalesmenAnalyticsIndicator.values)
        ]
    )
    def get(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        indicator = self.request.query_params.get('indicator', SalesmenAnalyticsIndicator.SALES_COUNT)
        result = SalesmenAnalyticsService(indicator, start_date, end_date).get_final_result_data()
        return Response(data=result)


class OutlaysAnalyticsView(DateRangeFilterMixin, ViewSet):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('indicator', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=OutlaysAnalyticsIndicator.values)
        ]
    )
    def get_chart_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        indicator = self.request.query_params.get('indicator', OutlaysAnalyticsIndicator.OUTCOME)
        result = OutlaysAnalyticService(indicator, start_date, end_date).get_chart_data()
        return Response(data=result)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('indicator', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=OutlaysAnalyticsIndicator.values)
        ]
    )
    def get_table_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        indicator = self.request.query_params.get('indicator', OutlaysAnalyticsIndicator.OUTCOME)
        result = OutlaysAnalyticService(indicator, start_date, end_date).get_table_data()
        return Response(data=result)


class WriteOffsAnalyticsView(DateRangeFilterMixin, ViewSet):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get_chart_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        result = WriteOffsAnalyticsService(start_date, end_date).get_chart_data()
        return Response(data=result)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get_tables_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        result = WriteOffsAnalyticsService(start_date, end_date).get_tables_data()
        return Response(data=result)


class ClientsAnalyticsViewSet(DateRangeFilterMixin, ViewSet):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('client_id', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Client ID"),

        ]
    )
    def get_chart_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        client_id = self.request.query_params.get('client_id')
        result = ClientsAnalyticsService(client_id, start_date, end_date).get_result_data()
        return Response(data=result)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('client_id', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Client ID"),
            openapi.Parameter('order_field', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=["total_orders_sum", "orders_count", "debt"]),
            openapi.Parameter('page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get_clients(self, request):
        start_date, end_date = self.get_start_end_dates()
        order_field = self.request.query_params.get('order_field')
        client_ids = self.request.query_params.getlist('client_id', default=None)
        serializer_context = {'order_field': order_field}

        service = ClientsTopAnalyticsService(order_field, client_ids, start_date, end_date)
        clients = service.get_annotated_clients()

        paginator = AnalyticsTablePagination()
        page = paginator.paginate_queryset(clients, request, self)
        if page:
            serializer = ClientAnalyticClientSerializer(page, many=True, context=serializer_context)
            return paginator.get_paginated_response(serializer.data)
        return Response(data=ClientAnalyticClientSerializer(clients, many=True, context=serializer_context).data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('client_id', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Client ID"),
            openapi.Parameter('order_field', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=["total_orders_sum", "orders_count", "debt"]),
            openapi.Parameter('page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get_linear_chart_data(self, request):
        start_date, end_date = self.get_start_end_dates()
        order_field = self.request.query_params.get('order_field')
        client_ids = self.request.query_params.getlist('client_id', default=None)

        service = ClientsTopAnalyticsService(order_field, client_ids, start_date, end_date)
        data = service.get_final_result_data()

        indicator_choices = [{"value": choice[0], "label": choice[1]} for choice in ClientsAnalyticsIndicator.choices]
        return Response({"data": data, "indicator_options": indicator_choices})


class FloristsIndicatorOptionsView(APIView):
    def get(self, request):
        indicator_choices = [{"value": choice[0], "label": choice[1]} for choice in FloristsAnalyticsIndicator.choices]
        return Response(data=indicator_choices)


class ProductIndicatorOptionsView(APIView):
    def get(self, request):
        indicator_choices = [{"value": choice[0], "label": choice[1]} for choice in ProductAnalyticsIndicator.choices]
        return Response(data=indicator_choices)


class SalesmenIndicatorOptionsView(APIView):
    def get(self, request):
        indicator_choices = [{"value": choice[0], "label": choice[1]} for choice in SalesmenAnalyticsIndicator.choices]
        return Response(data=indicator_choices)


class OutlaysIndicatorOptionsView(APIView):
    def get(self, request):
        indicator_choices = [{"value": choice[0], "label": choice[1]} for choice in OutlaysAnalyticsIndicator.choices]
        return Response(data=indicator_choices)


class ClientsIndicatorOptionsView(APIView):
    def get(self, request):
        indicator_choices = [{"value": choice[0], "label": choice[1]} for choice in ClientsAnalyticsIndicator.choices]
        return Response(data=indicator_choices)
