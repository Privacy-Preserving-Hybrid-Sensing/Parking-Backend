from django.db import models
from django.utils.timezone import now

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
