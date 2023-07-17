from enum import Enum
from django.db import models


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

class Order(models.Model):
    pass

class OrderStatus(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES.to_choice_values(), default='PENDING')
    order = models.ForeignKey(Order, related_name='order_statuses', on_delete=models.CASCADE)

class Order2(models.Model):
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES.to_choice_values())

    class Meta:
        indexes = [models.Index(fields=['current_status'])]

class OrderStatus2(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES.to_choice_values(), default='PENDING')
    order = models.ForeignKey(Order2, related_name='order_statuses', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(OrderStatus2, self).save(*args, **kwargs)
        
        # Update the current_status field of the related Order2 model
        self.order.current_status = self.status
        self.order.save()

