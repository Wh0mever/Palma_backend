from  rest_framework import serializers

from src.order.models import Client


class ClientAnalyticClientSerializer(serializers.ModelSerializer):
    aggregated_value = serializers.DecimalField(max_digits=19, decimal_places=2, allow_null=True)

    class Meta:
        model = Client
        fields = ('id', 'full_name', 'phone_number', 'aggregated_value')
