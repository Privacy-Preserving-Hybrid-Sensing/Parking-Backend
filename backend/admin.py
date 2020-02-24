from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.contrib import admin
from .models import ParkingZone, ParkingSpot, Subscription, ParkingZonePolygonGeoPoint, Participation, Profile, ParkingSpotHistory


class ParkingZoneResource(resources.ModelResource):
  class Meta:
    model = ParkingZone


class ParkingZoneAdmin(ImportExportModelAdmin):
  resource_class = ParkingZoneResource
  list_display = ['name', 'description', 'center_longitude', 'center_latitude', 'credit_required', 'token']

class ParkingZonePolygonGeoPointResource(resources.ModelResource):
  class Meta:
    model = ParkingZonePolygonGeoPoint
class ParkingZonePolygonGeoPointAdmin(ImportExportModelAdmin):
  resource_class = ParkingZonePolygonGeoPointResource
  list_display = ['parking_zone','longitude','latitude']

class ParkingSpotResource(resources.ModelResource):
  class Meta:
    model = ParkingSpot
class ParkingSpotAdmin(ImportExportModelAdmin):
  resource_class = ParkingSpotResource
  list_display = ['name', 'ts_register', 'ts_update','registrar_uuid','longitude','latitude','vote_available','vote_unavailable','confidence_level','parking_status','zone']

class ParkingSpotHistoryResource(resources.ModelResource):
  class Meta:
    model = ParkingSpotHistory
class ParkingSpotHistoryAdmin(ImportExportModelAdmin):
  resource_class = ParkingSpotHistoryResource
  list_display = ['name', 'ts_previous', 'ts_latest','registrar_uuid','longitude','latitude','vote_available','vote_unavailable','confidence_level','parking_status', 'parking_spot', 'zone']

class SubscriptionResource(resources.ModelResource):
  class Meta:
    model = Subscription
class SubscriptionAdmin(ImportExportModelAdmin):
  resource_class = SubscriptionResource
  list_display = ['ts','subscriber_uuid','zone','charged']

class ProfileResource(resources.ModelResource):
  class Meta:
    model = Profile
class ProfileAdmin(ImportExportModelAdmin):
  resource_class = ProfileResource
  list_display = ['ts','subscriber_uuid', 'email', 'key_validation', 'validated']

class ParticipationResource(resources.ModelResource):
  class Meta:
    model = Participation
class ParticipationAdmin(ImportExportModelAdmin):
  resource_class = ParticipationResource
  list_display = ['ts_update','participant_uuid', 'participation_value', 'incentive_processed','parking_spot', 'incentive_value']



admin.site.register(ParkingZone, ParkingZoneAdmin)
admin.site.register(ParkingZonePolygonGeoPoint, ParkingZonePolygonGeoPointAdmin)
admin.site.register(ParkingSpot, ParkingSpotAdmin)
admin.site.register(ParkingSpotHistory, ParkingSpotHistoryAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Profile, ProfileAdmin)
