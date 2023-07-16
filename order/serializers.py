
from django.db.models import fields
from rest_framework import serializers
from .models import Order, OrderStatus
 

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'
        exclude_fields = ['order']
        read_only_fields = [
            'id',
            'created_time',
        ]


class OrderSerializer(serializers.ModelSerializer):
    order_statuses = OrderStatusSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'order_statuses')