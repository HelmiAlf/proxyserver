from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("topupform/", views.topup_form, name="topup_form")
]