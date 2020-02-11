from django.contrib import admin
from .models import ParkingZone, ParkingSlot, ParkingAvailabilitySubscription, ParticipantCredit, ParkingZonePolygonGeoPoint

admin.site.register(ParkingZone)
admin.site.register(ParkingZonePolygonGeoPoint)
admin.site.register(ParkingSlot)
admin.site.register(ParkingAvailabilitySubscription)
admin.site.register(ParticipantCredit)

