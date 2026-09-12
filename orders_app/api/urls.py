from django.urls import path

from .views import CompletedOrderCountView, OrderCountView, OrderListCreateView, OrderUpdateView

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderUpdateView.as_view(), name="order-update"),
    path("order-count/<int:business_user_id>/", OrderCountView.as_view(), name="order-count"),
    path("completed-order-count/<int:business_user_id>/", CompletedOrderCountView.as_view(), name="completed-order-count"),
]
