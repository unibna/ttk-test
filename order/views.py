import django_filters.rest_framework
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from . import serializers
from . import models
from . import filters


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class CustomPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 1000
    page_size_query_param = 'page_size'

class OrderViewSet(ModelViewSet):
    serializer_class = serializers.OrderSerializer
    queryset = models.Order.objects.all()
    filterset_class = filters.CustomOrderFilter
    pagination_class = CustomPagination

class OrderStatusViewSet(ModelViewSet):
    serializer_class = serializers.OrderStatusSerializer
    queryset = models.OrderStatus.objects.all()

class OrderViewSet2(ModelViewSet):
    serializer_class = serializers.OrderSerializer2
    queryset = models.Order2.objects.all()
    pagination_class = CustomPagination
    filterset_class = filters.CustomOrder2Filter

    # @method_decorator(cache_page(CACHE_TTL))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)
    
    # @method_decorator(cache_page(CACHE_TTL))
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

class OrderStatusViewSet2(ModelViewSet):
    serializer_class = serializers.OrderStatusSerializer2
    queryset = models.OrderStatus2.objects.all()
