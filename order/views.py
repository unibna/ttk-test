import datetime
from rest_framework import (
    generics,
    status,
    exceptions,
    pagination
)
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from . import serializers
from . import models


# Caching config
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
LIMIT_THRESHOLD = 1_000


class OrderAPI(
    generics.GenericAPIView,
):
    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request, *args, **kwargs):
        if "id" in kwargs:
            ressponse = self._get_detail(request, *args, **kwargs)
        else:
            ressponse = self._listing(request, *args, **kwargs)
        return ressponse
    
    def _get_detail(self, request, *args, **kwargs):
        object_id = kwargs.get('id', '')
        order = models.Order.objects.get(pk=object_id)
        return JsonResponse({
            "order": serializers.OrderSerializer(order).data
        })

    def _listing(self, request, *args, **kwargs):
        # Get pagination info
        limit, page = self.get_pagination(request)
        
        # Handle filter
        q_objects = Q()
        if filter_value := request.query_params.get('status'):
            q_objects &= Q(order_statuses__status=filter_value)
        if filter_value := request.query_params.get('order_status_from'):
            q_objects &= Q(order_statuses__created_time__gte=filter_value)
        if filter_value := request.query_params.get('order_status_to'):
            q_objects &= Q(order_statuses__created_time__lte=filter_value)
        
        # Hadle sort
        if sort_value := request.query_params.get('sort_by'):
            orders_queryset = models.Order.objects.prefetch_related().filter(q_objects).order_by(sort_value)
        else:
            orders_queryset = models.Order.objects.prefetch_related().filter(q_objects)

        paginator = Paginator(orders_queryset, limit)
        data = serializers.OrderSerializer(paginator.page(page), many=True).data

        return JsonResponse({
            "pagination": {
                "limit": limit,
                "page": page,
            },
            "data": {
                "orders": data
            },
        })
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = serializers.OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            self.set_relations(
                order=order, 
                status=models.OrderStatus.STATUS_CHOICES.PENDING.value,
            )        

            return JsonResponse({
                "order": serializer.data
            })
        else:
            raise exceptions.ValidationError(
                detail="Invalid Payload"
            )
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        # Verify actions
        action = request.data.pop('payment_action')
        if action == 'payment_success':
            order_status = models.OrderStatus.STATUS_CHOICES.COMPLETED.value
        elif action == 'payment_fail':
            order_status = models.OrderStatus.STATUS_CHOICES.CANCELLED.value
        elif action == 'refund':
            order_status = models.OrderStatus.STATUS_CHOICES.CANCELLED.value
        else:
            raise exceptions.ValidationError(
                detail="Invalid Payment Action"
            )

        # Verify instance
        order: models.Order = self.get_object(*args, **kwargs)
        if models.Order.objects.filter(pk=order.id, order_statuses__status=order_status):
            raise exceptions.ValidationError(
                detail="This order can't be updated"
            )

        # Update
        serializer = serializers.OrderSerializer(order,request.data)
        if serializer.is_valid():
            order = serializer.save()
            self.set_relations(
                order=order, 
                status=order_status,
            )  

            return JsonResponse({
                "order": serializer.data
            })

    def set_relations(self, order, status):
        # Valid input
        if status not in models.OrderStatus.STATUS_CHOICES.to_list():
            raise exceptions.APIException()
        
        return models.OrderStatus.objects.create(
            status=status,
            order=order,
        )

    def get_object(self, *args, **kwargs):
        try:
            object_id = kwargs.get('id', '')
            order = models.Order.objects.get(pk=object_id)
            return order
        except:
            raise exceptions.NotFound()
            
    def get_pagination(self, request):
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 20))
        if limit > LIMIT_THRESHOLD:
            limit = LIMIT_THRESHOLD
        return limit, page
