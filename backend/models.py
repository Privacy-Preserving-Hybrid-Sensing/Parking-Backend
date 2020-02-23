from django.db import models
from django.utils.timezone import now
from datetime import datetime, timedelta, date
import uuid 

class ParkingZone(models.Model):
  name = models.CharField(max_length=100, db_index=True)
  ts_update = models.DateTimeField(default=now)
  description = models.CharField(max_length=1000, default="")
  center_longitude = models.CharField(max_length=100, default="0.0")
  center_latitude = models.CharField(max_length=100, default="0.0")
  credit_required = models.IntegerField(default=5)

  # Status Codes for ParkingSpot
  # case -3: MARKER_PARKING_UNAVAILABLE_CONFIRMED;
  # case -2: MARKER_PARKING_UNAVAILABLE_CONFIDENT_2;
  # case -1: MARKER_PARKING_UNAVAILABLE_CONFIDENT_1;
  # case 0: MARKER_PARKING_UNCONFIRMED;
  # case 1: MARKER_PARKING_AVAILABLE_CONFIDENT_1;
  # case 2: MARKER_PARKING_AVAILABLE_CONFIDENT_2;
  # case 3: MARKER_PARKING_AVAILABLE_CONFIRMED;

class ParkingSpot(models.Model):
  name = models.CharField(max_length=100, db_index=True, default="")
  ts_register = models.DateTimeField(default=now)
  ts_update = models.DateTimeField(default=now)
  registrar_uuid = models.CharField(max_length=100)
  longitude = models.CharField(max_length=100, default="0.0")
  latitude = models.CharField(max_length=100, default="0.0")
  vote_available = models.IntegerField(default=0)
  vote_unavailable = models.IntegerField(default=0)
  confidence_level = models.FloatField(default=0)
  status = models.IntegerField(default=0)
  zone = models.ForeignKey(ParkingZone, on_delete=models.CASCADE, blank=True, null=True)
  class Meta:
    unique_together = (('longitude', 'latitude'),)

  def change(longitude, latitude, vote_available, vote_unavailable, status, confidence_level):
    change_status = "unchanged"
    current_data = ParkingSpot.objects.filter(longitude = longitude, latitude = latitude).first()
    if current_data.vote_available != vote_available or current_data.vote_unavailable != vote_unavailable or current_data.status != status:
      current_data.vote_available = vote_available
      current_data.vote_unavailable = vote_unavailable
      current_data.confidence_level = confidence_level
      current_data.status = status
      current_data.ts_update = datetime.now()
      current_data.save()
      ParkingSpotChanges(parking_spot=current_data, longitude=longitude, latitude=latitude, vote_available=vote_available, vote_unavailable=vote_unavailable, status=status, confidence_level=confidence_level)
      change_status = "changed"

    return change_status

  def create(registrar_uuid, longitude, latitude, zone):
    current_data = ParkingSpot.objects.filter(longitude = longitude, latitude = latitude).first()
    if current_data == None:
      new_data = ParkingSpot(
        registrar_uuid = registrar_uuid,
        longitude = longitude,
        latitude = latitude,
        vote_available = 0,
        vote_unavailable = 0,
        confidence_level=0,
        status = 0,
        zone = zone
      )
      new_data.save()
      parking_changes = ParkingSpotChanges(
        parking_spot = new_data,
        longitude = longitude,
        latitude = latitude,
        vote_available = 0,
        vote_unavailable = 0,
        confidence_level = 0,
        status = 0,
      )
      parking_changes.save()

class ParkingZonePolygonGeoPoint(models.Model):
  parking_zone = models.ForeignKey(ParkingZone, on_delete=models.CASCADE, blank=True, null=True)
  longitude = models.CharField(max_length=100)
  latitude = models.CharField(max_length=100)

class ParkingSpotChanges(models.Model):
  parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, blank=True, null=True)
  ts_change = models.DateTimeField(default=now)
  longitude = models.CharField(max_length=100, default="0.0", db_index=True)
  latitude = models.CharField(max_length=100, default="0.0", db_index=True)
  vote_available = models.IntegerField(default=0)
  vote_unavailable = models.IntegerField(default=0)
  confidence_level = models.FloatField(default=0)
  status = models.IntegerField(default=0)
  class Meta:
    unique_together = (('longitude', 'latitude', 'ts_change'),)

class ParticipantMovementLog(models.Model):
  ts = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100, db_index=True)
  longitude = models.CharField(max_length=100, default="0.0")
  latitude = models.CharField(max_length=100, default="0.0")

class ParkingAvailabilityLog(models.Model):
  ts = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100, db_index=True)
  longitude = models.CharField(max_length=100, default="0.0")
  latitude = models.CharField(max_length=100, default="0.0")
  participation_value = models.FloatField(default=0)
  parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, blank=True, null=True)

class Participation(models.Model):
  ts_create = models.DateTimeField(default=now)
  ts_update = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100, db_index=True)
  participation_value = models.FloatField()
  processed = models.BooleanField(default=False)
  parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, blank=True, null=True)
  incentive_value = models.IntegerField(default=0)

  def participate(parking_spot, participant_uuid, participation_value, minute_treshold):
    time_treshold = datetime.now() - timedelta(minutes=minute_treshold)
    participation_data = Participation.objects.filter(ts_update__gt=time_treshold, parking_spot=parking_spot, participant_uuid=participant_uuid).first()

    if participation_data == None:
      participation_data = Participation(participant_uuid=participant_uuid, participation_value=participation_value, parking_spot=parking_spot)
      participation_data.save()
    else:
      participation_data.ts_update = datetime.now()
      participation_data.participation_value = participation_value
      participation_data.processed = False
      participation_data.incentive_value = 0
      participation_data.save()

    return participation_data

class Subscription(models.Model):
  ts = models.DateTimeField(default=now)
  subscriber_uuid = models.CharField(max_length=100, db_index=True)
  zone = models.ForeignKey(ParkingZone, on_delete=models.CASCADE, blank=True, null=True)
  charged = models.IntegerField(default=0)


class Profile(models.Model):
  ts = models.DateTimeField(default=now)
  subscriber_uuid = models.CharField(max_length=100, db_index=True)
  email = models.CharField(max_length=100, db_index=True)
  key_validation = models.CharField(max_length=200, db_index=True)
  validated = models.BooleanField(default=False)
  class Meta:
    unique_together = (('subscriber_uuid', 'email'),)

  def register(subscriber_uuid, email):
    profile_by_email_uuid = Profile.objects.filter(email=email, subscriber_uuid=subscriber_uuid).first()
    if profile_by_email_uuid is None:
      key_validation = uuid.uuid1()
      profile_by_email_uuid = Profile(subscriber_uuid=subscriber_uuid, email=email,key_validation=key_validation)
      profile_by_email_uuid.save()
    return profile_by_email_uuid