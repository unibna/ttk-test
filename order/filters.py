import django_filters
from django.db.models import OuterRef, Subquery
from .models import Order, OrderStatus


class CustomOrderFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(method='filter_status')

    class Meta:
        model = Order
        fields = ['status']

    def filter_status(self, queryset, name, value):
        # Create a subquery to get the latest order status for each order
        latest_status_subquery = OrderStatus.objects.\
            filter(order=OuterRef('pk')).\
            order_by('-created_time').\
            values('status')[:1]

        # Query all orders and annotate with the latest status
        orders_with_latest_status = Order.objects.annotate(latest_status=Subquery(latest_status_subquery))
        cancelled_orders = orders_with_latest_status.filter(latest_status=value)

        return cancelled_orders


