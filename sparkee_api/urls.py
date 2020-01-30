from django.contrib import admin
from django.urls import include, path, re_path
from .views import parking_slots_near, summary_near, summary_all

urlpatterns = [
    re_path(r"^parking_slots/near/(?P<radius>[0-9\.]+)/(?P<longitude>[0-9\.\+\-]+)/(?P<lattitude>[0-9\.\+\-]+)$", parking_slots_near, name="api_parking_slots_near"),
    re_path(r"^summary/near/(?P<radius>[0-9\.]+)/(?P<longitude>[0-9\.\+\-]+)/(?P<lattitude>[0-9\.\+\-]+)$", summary_near, name="api_summary_near"),
    path("summary/all", summary_all, name="api_summary_all"),
]
