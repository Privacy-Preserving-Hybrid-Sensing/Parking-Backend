from django.contrib import admin
from django.urls import include, path
from .views import index, validation_key

urlpatterns = [
    path('', index),
    path("validation/<str:key>", validation_key, name="zones_search_keyword"), ##
]
