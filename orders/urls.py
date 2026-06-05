from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/payment/", views.payment, name="payment"),
    path("checkout/review/", views.review, name="review"),
    path("place/", views.place, name="place"),
    path("confirmation/<str:number>/", views.confirmation, name="confirmation"),
    path("history/", views.history, name="history"),
    path("history/<str:number>/", views.order_detail, name="order_detail"),
    path("addresses/", views.address_list, name="address_list"),
    path("addresses/add/", views.address_add, name="address_add"),
    path("addresses/<int:pk>/edit/", views.address_edit, name="address_edit"),
    path("addresses/<int:pk>/delete/", views.address_delete, name="address_delete"),
]
