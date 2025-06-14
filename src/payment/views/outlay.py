from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from src.base.api_views import MultiSerializerViewSetMixin, DestroyFlagsViewSetMixin, CustomPagination
from src.base.filter_backends import CustomDateRangeFilter
from src.payment.enums import OutlayType, PaymentModelType
from src.payment.models import Outlay, Payment
from src.payment.serializers.outlay import OutlayListSerializer, OutlayDetailSerializer, OutlayCreateSerializer
from src.payment.serializers.payment import PaymentListSerializer


class OutlayViewSet(MultiSerializerViewSetMixin, DestroyFlagsViewSetMixin, ModelViewSet):
    queryset = Outlay.objects.get_available()
    serializer_action_classes = {
        'list': OutlayListSerializer,
        'retrieve': OutlayDetailSerializer,
        'create': OutlayCreateSerializer,
        'partial_update': OutlayCreateSerializer,
    }
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_fields = ['outlay_type']
    search_fields = ('id', 'comment')

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related(Prefetch('payments', queryset=Payment.objects.get_available()))
        return qs

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user)


class OutlayPaymentListView(ListAPIView):
    serializer_class = PaymentListSerializer
    queryset = Payment.objects.get_available().filter(payment_model_type=PaymentModelType.OUTLAY).prefetch_related(
        'created_user', 'order', 'client'
    )
    pagination_class = CustomPagination
    filter_backends = [
        # CustomDateRangeFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = ['payment_method', 'payment_type', 'payment_model_type']
    filter_date_field = 'created_at',
    date_filter_ignore_actions = [
        'create', 'partial_update', 'update', 'destroy', 'retrieve'
    ]

    def get_outlay(self):
        outlay_id = self.kwargs.get('pk')
        outlay = get_object_or_404(Outlay, pk=outlay_id)
        return outlay

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(outlay=self.get_outlay())
        return qs


class OutlayTypeOptionsView(APIView):
    def get(self, request):
        outlay_type_choices = [{"value": choice[0], "label": choice[1]} for choice in OutlayType.choices]
        return Response(outlay_type_choices, status=200)
