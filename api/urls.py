from django.contrib import admin
from django.urls import include, path, re_path
from .views import summary_all
from .views import zones_all, zones_id, zones_search_keyword, zones_id_spots_all, zones_id_spots_id, zones_id_subscribe
from .views import profile_creditbalance, profile_participations_days_ago, profile_register_email
from .views import participate_zone_spot_status
# from .views import parking_spots_get_all, parking_spots_get_id, parking_spots_search

urlpatterns = [
    path("summary/all", summary_all, name="api_summary_all"),
    path("zones/<int:zone_id>/spots/all", zones_id_spots_all, name="zones_id_spots_all"), ##
    path("zones/<int:zone_id>/spots/<int:spot_id>", zones_id_spots_id, name="zones_id_spots_id"), ##
    path("zones/<int:zone_id>/subscribe", zones_id_subscribe, name="zones_id_subscribe"), ##
    path("zones/<int:zone_id>", zones_id, name="zones_id"), ##
    path("zones/search/<str:keyword>", zones_search_keyword, name="zones_search_keyword"), ##
    path("zones/all", zones_all, name="zones_all"), ##

    path("profile/creditbalance", profile_creditbalance, name="profile_creditbalance"),
    path("profile/participations/<int:days_ago>", profile_participations_days_ago, name="profile_participations_days_ago"),
    path("participate/<int:zone_id>/<int:spot_id>/<str:status>", participate_zone_spot_status, name="participate_zone_spot_status"),
    path("profile/register/<str:email>", profile_register_email, name="profile_register_email"),
]
