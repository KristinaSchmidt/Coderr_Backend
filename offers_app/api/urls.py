from django.urls import path

from .views import BaseInfoView, OfferDetailRetrieveView, OfferDetailView, OfferListCreateView

urlpatterns = [
    path("offers/", OfferListCreateView.as_view(), name="offer-list"),
    path("offers/<int:pk>/", OfferDetailView.as_view(), name="offer-detail"),
    path("offerdetails/<int:pk>/", OfferDetailRetrieveView.as_view(), name="offer-detail-item"),
    path("base-info/", BaseInfoView.as_view(), name="base-info"),
]
