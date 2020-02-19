from django.db import models
from django.utils.timezone import now
from datetime import datetime, timedelta, date

class ParkingZone(models.Model):
  name = models.CharField(max_length=100, db_index=True)
  ts_update = models.DateTimeField(default=now)
  description = models.CharField(max_length=1000, default="")
  center_longitude = models.CharField(max_length=100, default="0.0")
  center_latitude = models.CharField(max_length=100, default="0.0")
  credit_charge = models.IntegerField(default=5)

  # Status Codes for ParkingSpot
  # case -3: MARKER_PARKING_UNAVAILABLE_CONFIRMED;
  # case -2: MARKER_PARKING_UNAVAILABLE_CONFIDENT_2;
  # case -1: MARKER_PARKING_UNAVAILABLE_CONFIDENT_1;
  # case 0: MARKER_PARKING_UNCONFIRMED;
  # case 1: MARKER_PARKING_AVAILABLE_CONFIDENT_1;
  # case 2: MARKER_PARKING_AVAILABLE_CONFIDENT_2;
  # case 3: MARKER_PARKING_AVAILABLE_CONFIRMED;

class ParkingSpot(models.Model):
  ts_register = models.DateTimeField(default=now)
  ts_update = models.DateTimeField(default=now)
  registrar_uuid = models.CharField(max_length=100)
  longitude = models.CharField(max_length=100, default="0.0")
  latitude = models.CharField(max_length=100, default="0.0")
  voting_available = models.FloatField(default=0)
  voting_unavailable = models.FloatField(default=0)
  confidence_level = models.FloatField(default=0)
  status = models.IntegerField(default=0)
  zone = models.ForeignKey(ParkingZone, on_delete=models.CASCADE, blank=True, null=True)
  class Meta:
    unique_together = (('longitude', 'latitude'),)

  def change(longitude, latitude, voting_available, voting_unavailable, status, confidence_level):
    change_status = "unchanged"
    current_data = ParkingSpot.objects.filter(longitude = longitude, latitude = latitude).first()
    if current_data.voting_available != voting_available or current_data.voting_unavailable != voting_unavailable or current_data.status != status:
      current_data.voting_available = voting_available
      current_data.voting_unavailable = voting_unavailable
      current_data.confidence_level = confidence_level
      current_data.status = status
      current_data.ts_update = datetime.now()
      current_data.save()
      ParkingSpotChanges(parking_spot=current_data, longitude=longitude, latitude=latitude, voting_available=voting_available, voting_unavailable=voting_unavailable, status=status, confidence_level=confidence_level)
      change_status = "changed"

    return change_status

  def create(registrar_uuid, longitude, latitude, zone):
    current_data = ParkingSpot.objects.filter(longitude = longitude, latitude = latitude).first()
    if current_data == None:
      new_data = ParkingSpot(
        registrar_uuid = registrar_uuid,
        longitude = longitude,
        latitude = latitude,
        voting_available = 0,
        voting_unavailable = 0,
        confidence_level=0,
        status = 0,
        zone = zone
      )
      new_data.save()
      parking_changes = ParkingSpotChanges(
        parking_spot = new_data,
        longitude = longitude,
        latitude = latitude,
        voting_available = 0,
        voting_unavailable = 0,
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
  voting_available = models.FloatField(default=0)
  voting_unavailable = models.FloatField(default=0)
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
  availability_value = models.FloatField(default=0)
  parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, blank=True, null=True)

class Participation(models.Model):
  ts_update = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100, db_index=True)
  longitude = models.CharField(max_length=100, default="0.0", db_index=True)
  latitude = models.CharField(max_length=100, default="0.0", db_index=True)
  availability_value = models.FloatField()
  processed = models.BooleanField(default=False)
  parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, blank=True, null=True)

  def participate(parking_spot, participant_uuid, availability_value, minute_treshold):
    time_treshold = datetime.now() - timedelta(minutes=minute_treshold)
    previous_participation_data_in_time_threshold = Participation.objects.filter(ts_update__gt=time_treshold, parking_spot=parking_spot, participant_uuid=participant_uuid).first()

    new_participation_status = False
    current_time = datetime.now()
    if previous_participation_data_in_time_threshold == None:
      new_participation_data = Participation(participant_uuid=participant_uuid, longitude=parking_spot.longitude, latitude=parking_spot.latitude, availability_value=availability_value, parking_spot=parking_spot)
      new_participation_data.save()
      new_participation_status = True
      new_credit_data = ParticipantCredit(participant_uuid=participant_uuid, participation=new_participation_data)
      new_credit_data.save()
    else:
      previous_credit = ParticipantCredit.objects.filter(participation=previous_participation_data_in_time_threshold).first()
      previous_credit.ts_update = current_time
      previous_credit.point = 0          # reset to 0 when updated
      previous_credit.processed = False         # reset to False when updated
      previous_credit.save()
      previous_participation_data_in_time_threshold.ts_update = current_time
      previous_participation_data_in_time_threshold.availability_value = availability_value
      previous_participation_data_in_time_threshold.save()

    return new_participation_status, current_time

class ParticipantCredit(models.Model):
  ts_update = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100, db_index=True)
  credit_value = models.IntegerField(default=0)
  participation = models.ForeignKey(Participation, on_delete=models.CASCADE, blank=True, null=True)

class Subscription(models.Model):
  ts = models.DateTimeField(default=now)
  subscriber_uuid = models.CharField(max_length=100, db_index=True)
  zone = models.ForeignKey(ParkingZone, on_delete=models.CASCADE, blank=True, null=True)
  credit_charged = models.IntegerField(default=0)

