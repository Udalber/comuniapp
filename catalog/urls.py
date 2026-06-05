from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.index, name="index"),
    path("suggest/", views.suggest, name="suggest"),
    path("<slug:slug>/", views.detail, name="detail"),
]
