from django.contrib import admin
from django.urls import include, path, re_path
from .views import summary_all
# from .views import parking_slots_near, summary_near, summary_all, subscribe_parking_availability

urlpatterns = [
    path("summary/all", summary_all, name="api_summary_all"),
]
