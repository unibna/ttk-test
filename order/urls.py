from django.urls import path, include
from rest_framework import routers
from . import views


order_route = routers.DefaultRouter()
order_route.register("order", views.OrderViewSet, basename="order")

order_status_route = routers.DefaultRouter()
order_status_route.register("order-status", views.OrderStatusViewSet, basename="order-status")

order_route2 = routers.DefaultRouter()
order_route2.register("order-2", views.OrderViewSet2, basename="order-2")

order_status_route2 = routers.DefaultRouter()
order_status_route2.register("order-status-2", views.OrderStatusViewSet2, basename="order-status-2")

urlpatterns = [
    path("", include(order_route.urls)),
    path("", include(order_status_route.urls)),
    path("", include(order_route2.urls)),
    path("", include(order_status_route2.urls)),
]