from django.db import models
from django.utils.timezone import now
from datetime import datetime, timedelta, date

class ParkingZone(models.Model):
  name = models.CharField(max_length=100, db_index=True)
  description = models.CharField(max_length=1000, default="")
  center_longitude = models.CharField(max_length=100, default="0.0")
  center_latitude = models.CharField(max_length=100, default="0.0")

class ParkingSlot(models.Model):
  ts_register = models.DateTimeField(default=now)
  ts_update = models.DateTimeField(default=now)
  registrar_uuid = models.CharField(max_length=100)
  longitude = models.CharField(max_length=100, default="0.0", db_index=True)
  latitude = models.CharField(max_length=100, default="0.0", db_index=True)
  total_available = models.FloatField(default=0)
  total_unavailable = models.FloatField(default=0)
  status = models.IntegerField(default=0)
  zone = models.ForeignKey(ParkingZone, on_delete=models.CASCADE, blank=True, null=True)

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

class DataParticipationParkingAvailability(models.Model):
  ts_update = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100, db_index=True)
  longitude = models.CharField(max_length=100, default="0.0")
  latitude = models.CharField(max_length=100, default="0.0")
  availability_value = models.FloatField()
  processed = models.BooleanField(default=False)
  parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, blank=True, null=True)

  def participate(longitude, latitude, participant_uuid, availability_value, minute_treshold):
    time_treshold = datetime.now() - timedelta(minutes=minute_treshold)
    previous_participation_data_in_time_threshold = DataParticipationParkingAvailability.objects.filter(ts_update__gt=time_treshold, longitude=longitude, latitude=latitude, participant_uuid=participant_uuid).first()

    new_participation_status = False
    current_time = datetime.now()
    if previous_participation_data_in_time_threshold == None:
      related_parking_slot = ParkingSlot.objects.filter(longitude=longitude, latitude=latitude).first()
      # print("RELATED PARKING SLOOOOOOOOOOOOOOT Lon: " + str(longitude) + ", Lat: " + str(latitude) )
      # print(related_parking_slot)
      new_participation_data = DataParticipationParkingAvailability(participant_uuid=participant_uuid, longitude=longitude, latitude = latitude, availability_value=availability_value, parking_slot=related_parking_slot)
      new_participation_data.save()
      new_participation_status = True
      new_credit_data = ParticipantCredit(participant_uuid=participant_uuid, participation=new_participation_data)
      new_credit_data.save()
    else:
      previous_credit = ParticipantCredit.objects.filter(participation=previous_participation_data_in_time_threshold).first()
      previous_credit.ts_update = current_time
      previous_credit.credit_value = 0          # reset to 0 when updated
      previous_credit.processed = False         # reset to False when updated
      previous_credit.save()
      previous_participation_data_in_time_threshold.ts_update = current_time
      previous_participation_data_in_time_threshold.availability_value = availability_value
      previous_participation_data_in_time_threshold.save()

    return new_participation_status, current_time

class ParticipantCredit(models.Model):
  ts_update = models.DateTimeField(default=now)
  participant_uuid = models.CharField(max_length=100, db_index=True)
  credit_value = models.FloatField(default=100)
  processed = models.BooleanField(default=False)
  participation = models.ForeignKey(DataParticipationParkingAvailability, on_delete=models.CASCADE, blank=True, null=True)

class InterimParkingAvailability(models.Model):
  ts_from = models.DateTimeField(default=now)
  ts_to = models.DateTimeField(default=now)
  longitude = models.CharField(max_length=100, default="0.0")
  latitude = models.CharField(max_length=100, default="0.0")
  total_available = models.FloatField(default=0)
  total_unavailable = models.FloatField(default=0)
  status = models.IntegerField(default=0)




class ParkingAvailabilitySubscription(models.Model):
  ts = models.DateTimeField(default=now)
  subscriber_uuid = models.CharField(max_length=100, db_index=True, unique=True)
  longitude = models.CharField(max_length=100, default="0.0")
  latitude = models.CharField(max_length=100, default="0.0")
  subscriber_type = models.CharField(max_length=100, db_index=True, default="web")

  def subscribe(longitude, latitude, subscriber_uuid, subscriber_type):
    data = ParkingAvailabilitySubscription.objects.filter(subscriber_uuid=subscriber_uuid).first()

    new_subscription_status = False
    current_time = datetime.now()
    if data == None:
      new_data = ParkingAvailabilitySubscription(subscriber_uuid=subscriber_uuid, longitude=longitude, latitude = latitude, subscriber_type=subscriber_type)
      new_data.save()
      new_subscription_status = True
    else:
      data.ts = current_time
      data.longitude = longitude
      data.latitude = latitude
      data.save()

    return new_subscription_status, current_time