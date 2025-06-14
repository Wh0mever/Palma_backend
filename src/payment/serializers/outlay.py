from rest_framework import serializers

from src.base.serializers import DynamicFieldsModelSerializer
from src.payment.models import Outlay
from src.product.serializers import IndustrySerializer


class OutlayListSerializer(DynamicFieldsModelSerializer):
    industry = IndustrySerializer(read_only=True)

    class Meta:
        model = Outlay
        fields = ('id', 'title', 'outlay_type', 'industry', 'created_at', 'created_user', 'comment')


class OutlayDetailSerializer(serializers.ModelSerializer):
    from src.payment.serializers.payment import PaymentListSerializer
    payments = PaymentListSerializer(many=True)
    industry = IndustrySerializer(read_only=True)

    class Meta:
        model = Outlay
        fields = ('id', 'title', 'outlay_type', 'industry', 'created_at', 'created_user', 'comment', 'payments')


class OutlayCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlay
        fields = ('title', 'outlay_type', 'comment', 'industry')

    def to_representation(self, instance):
        return OutlayDetailSerializer(instance=instance).data
