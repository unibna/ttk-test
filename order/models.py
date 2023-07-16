from enum import Enum
from django.db import models


class Order(models.Model):
    id = models.AutoField(primary_key=True)


class OrderStatus(models.Model):

    class STATUS_CHOICES(Enum):
        PENDING = 'PENDING'
        COMPLETED = 'COMPLETED'
        CANCELLED = 'CANCELLED'
    
        @classmethod
        def to_choice_values(cls):
            return [(x.value, x.value.capitalize()) for x in cls]
        
        @classmethod
        def to_list(cls):
            return [x.value for x in cls]


    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES.to_choice_values())
    order = models.ForeignKey(Order, related_name='order_statuses', on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_time', 'order_id'])
        ]

