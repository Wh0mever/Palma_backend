from django.db import models
from rest_framework import serializers

from src.payment.models import Cashier, CashierShift
from src.user.serializers import UserSerializer


class CashierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cashier
        fields = "__all__"


class CashierShiftSerializer(serializers.ModelSerializer):
    started_user = UserSerializer(read_only=True)
    completed_user = UserSerializer(read_only=True)

    class Meta:
        model = CashierShift
        fields = ('id', 'start_date', 'end_date', 'started_user', 'completed_user')
        read_only_fields = ('id', 'start_date', 'end_date', 'started_user', 'completed_user')


class CashierShiftListSerializer(CashierShiftSerializer):
    total_profit = serializers.DecimalField(source='get_total_profit', read_only=True, max_digits=19, decimal_places=2)
    total_profit_cash = serializers.DecimalField(source='get_total_profit_cash', read_only=True, max_digits=19, decimal_places=2)

    class Meta:
        model = CashierShift
        fields = CashierShiftSerializer.Meta.fields + (
            'overall_income_amount',
            'overall_outcome_amount',
            'cash_income_amount',
            'cash_outcome_amount',
            'total_profit',
            'total_profit_cash',
        )


class CashierShiftSummaryPageSerializer(serializers.Serializer):
    total_income_sum = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    total_outcome_sum = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    total_profit_sum = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    # payment_categories = serializers.ListField(read_only=True)
    shifts = CashierShiftListSerializer(many=True)
