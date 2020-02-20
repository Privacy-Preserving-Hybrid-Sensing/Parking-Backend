from django.contrib import admin
from django.urls import include, path, re_path
from .views import summary_all
from .views import parking_zones_info_all, parking_zones_info_id, parking_zones_search, parking_zones_subscribe, parking_zones_detail
from .views import participate_parking_spot
from .views import profile_creditbalance, profile_participation
# from .views import parking_spots_get_all, parking_spots_get_id, parking_spots_search

urlpatterns = [
    path("summary/all", summary_all, name="api_summary_all"),
    path("zones/info/all", parking_zones_info_all, name="api_parking_zones_info_all"),
    path("zones/info/<int:id>", parking_zones_info_id, name="api_parking_zones_info_id"),
    path("zones/info/search/<keyword>", parking_zones_search, name="api_parking_zones_search"),
    path("zones/detail/<int:zone_id>", parking_zones_detail, name="api_parking_zones_detail"),
    path("zones/subscribe/<int:zone_id>", parking_zones_subscribe, name="api_parking_zones_subscribe"),
    path("participate/<slug:status>/<int:parking_spot_id>", participate_parking_spot, name="api_participate_parking_spot"),
    path("profile/credit", profile_creditbalance, name="api_profile_credit"),   # DEPRECATED, it will be removed soon => to be creditbalance
    path("profile/creditbalance", profile_creditbalance, name="api_profile_creditbalance"),
    path("profile/participation/<int:days_ago>", profile_participation, name="api_profile_participation"),
    # path("profile/activity", profile_activity, name="api_profile_activity"),
]
