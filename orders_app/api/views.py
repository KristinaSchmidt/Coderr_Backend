"""Views for order creation, listing, status and counters."""

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order
from .permissions import IsBusinessOrderOwner, IsCustomerUser
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
)


class OrderListCreateView(generics.ListCreateAPIView):
    """List a user's orders or create an order as a customer."""

    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Return orders where the user is customer or business partner."""
        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        )

    def get_serializer_class(self):
        """Use the compact input serializer only for POST."""
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def get_permissions(self):
        """Restrict creation to customers while GET needs only auth."""
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Create and return the complete order with HTTP 201."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output = OrderSerializer(order)
        return Response(output.data, status=status.HTTP_201_CREATED)


class OrderUpdateView(generics.UpdateAPIView):
    """Allow the responsible business user to patch order status."""

    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = [IsAuthenticated, IsBusinessOrderOwner]
    http_method_names = ["patch", "head", "options"]

    def update(self, request, *args, **kwargs):
        """Save a valid status and return the complete updated order."""
        order = self.get_object()
        serializer = self.get_serializer(
            order,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)


class OrderCountView(APIView):
    """Return the number of in-progress orders for a business user."""

    permission_classes = [IsAuthenticated]
    status_value = Order.IN_PROGRESS

    response_key = "order_count"

    def get(self, request, business_user_id):
        """Count matching orders and return 404 for an unknown user."""
        get_object_or_404(User, pk=business_user_id)
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status=self.status_value,
        ).count()
        return Response({self.response_key: count})


class CompletedOrderCountView(OrderCountView):
    """Return the number of completed orders for a business user."""

    status_value = Order.COMPLETED
    response_key = "completed_order_count"
