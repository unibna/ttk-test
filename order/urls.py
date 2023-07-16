from django.urls import path

from . import views

urlpatterns = [
    # Order
    path('', views.OrderAPI.as_view()),
    path('/<int:id>', views.OrderAPI.as_view()),

    # Order Staus
    path('/status/<int:id>', views.OrderAPI.as_view()),
]

