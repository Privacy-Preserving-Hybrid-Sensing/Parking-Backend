from django.db import models
from django.utils.timezone import now
from datetime import datetime

class ParticipantMovementLog(models.Model):
  ts = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100)
  longitude = models.FloatField()
  lattitude = models.FloatField()

class ParkingAvailabilityLog(models.Model):
  ts = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100)
  longitude = models.FloatField()
  lattitude = models.FloatField()
  value = models.FloatField()

class ParkingSlot(models.Model):
  ts_register = models.DateTimeField(default=now)
  ts_update = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100)
  longitude = models.FloatField()
  lattitude = models.FloatField()
  confidence_available = models.FloatField(default=0)
  confidence_unavailable = models.FloatField(default=0)

class ParkingAvailabilitySubscription(models.Model):
  ts = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100)
  longitude = models.FloatField()
  lattitude = models.FloatField()
  radius = models.FloatField()

  def subscribe(radius, longitude, lattitude, participant_uuid):
    data = ParkingAvailabilitySubscription.objects.filter(participant_uuid=participant_uuid).first()

    status = ""
    current_time = datetime.now()
    if data == None:
      new_data = ParkingAvailabilitySubscription(participant_uuid=participant_uuid, radius=radius, longitude=longitude, lattitude = lattitude)
      new_data.save()
      status = "new"
    else:
      data.ts = current_time
      data.radius = radius
      data.longitude = longitude
      data.lattitude = lattitude
      data.save()
      status = "renew"

    return status, current_time