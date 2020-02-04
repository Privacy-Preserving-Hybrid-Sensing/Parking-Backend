from django.contrib import admin
from django.urls import include, path, re_path
from .views import summary_all
# from .views import parking_slots_near, summary_near, summary_all, subscribe_parking_availability

urlpatterns = [
    # re_path(r"^parking_slots/near/(?P<longitude>[0-9\.\+\-]+)/(?P<lattitude>[0-9\.\+\-]+)$", parking_slots_near, name="api_parking_slots_near"),

    # re_path(r"^subscribe/parking_availability/near/(?P<longitude>[0-9\.\+\-]+)/(?P<lattitude>[0-9\.\+\-]+)/(?P<subscriber_uuid>[0-9a-f\-]+)$", subscribe_parking_availability, name="subscribe_parking_availability"),

    path("summary/all", summary_all, name="api_summary_all"),
    # re_path(r"^summary/near/(?P<longitude>[0-9\.\+\-]+)/(?P<lattitude>[0-9\.\+\-]+)$", summary_near, name="api_summary_near"),
    
]
