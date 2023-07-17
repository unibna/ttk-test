from rest_framework import serializers
from . import models


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderStatus
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    order_statuses = OrderStatusSerializer(many=True, read_only=True)

    class Meta:
        model = models.Order
        fields = "__all__"

class OrderStatusSerializer2(serializers.ModelSerializer):
    class Meta:
        model = models.OrderStatus2
        fields = "__all__"

class OrderSerializer2(serializers.ModelSerializer):
    class Meta:
        model = models.Order2
        fields = "__all__"
