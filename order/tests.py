from django.test import TestCase
from rest_framework.test import APIClient
from order.models import (
    Order,
    OrderStatus,
    Order2,
    OrderStatus2,
    STATUS_CHOICES
)
from order import filters


class OrderTestCase(TestCase):

    def setUp(self) -> None:
        order_1 = Order.objects.create()
        OrderStatus.objects.create(order=order_1, status=STATUS_CHOICES.PENDING.value)
        OrderStatus.objects.create(order=order_1, status=STATUS_CHOICES.CANCELLED.value)

        order_2 = Order.objects.create()
        OrderStatus.objects.create(order=order_2, status=STATUS_CHOICES.PENDING.value)
        OrderStatus.objects.create(order=order_2, status=STATUS_CHOICES.COMPLETED.value)

        order_3 = Order.objects.create()
        OrderStatus.objects.create(order=order_3, status=STATUS_CHOICES.PENDING.value)
        OrderStatus.objects.create(order=order_3, status=STATUS_CHOICES.COMPLETED.value)
        OrderStatus.objects.create(order=order_3, status=STATUS_CHOICES.CANCELLED.value)

        order_4 = Order.objects.create()
        OrderStatus.objects.create(order=order_4, status=STATUS_CHOICES.PENDING.value)
        OrderStatus.objects.create(order=order_4, status=STATUS_CHOICES.CANCELLED.value)

        order_5 = Order.objects.create()
        OrderStatus.objects.create(order=order_5, status=STATUS_CHOICES.PENDING.value)

    def test_filter_status(self):
        status_value = STATUS_CHOICES.CANCELLED.value
        f = filters.CustomOrderFilter({'status': status_value}, queryset=Order.objects.all())
        f_queryset = f.qs

        self.assertEqual(f_queryset.count(), 3)
        for order in f_queryset.all():
            self.assertEqual(order.latest_status, status_value)
