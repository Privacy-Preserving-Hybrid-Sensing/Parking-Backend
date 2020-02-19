from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg, Max, Min, Sum
from django.db.models import Q
from backend.models import ParkingSpot, Participation, ParkingZone, ParkingZonePolygonGeoPoint, ParticipantCredit, Subscription, ParkingAvailabilityLog
import json
from django.core import serializers
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date
from .decorators import required_field

DEFAULT_MINUTE_THRESHOLD = 1

def summary_all(request):

    cnt_parking_spots = ParkingSpot.objects.distinct('latitude','longitude').count()
    cnt_participants = Participation.objects.distinct('participant_uuid').count()
    cnt_parking_zones = ParkingZone.objects.all().count()

    send = {
      'participants': cnt_participants,
      'parking_spots': cnt_parking_spots,
      'parking_zones': cnt_parking_zones
    }
    msg = "Summary OK"
    return generate_dict_response_ok(request, msg, send)

def parking_zones_search(request, keyword):
    arr_keyword = keyword.split(" ")
    q_object = Q()
    for word in arr_keyword:
      q_object = q_object & (Q(name__icontains=word)|Q(description__icontains=word))
    parking_zones = ParkingZone.objects.filter(q_object).values('id', 'name', 'description', 'center_longitude', 'center_latitude', 'credit_charge')
    msg = "Search " + keyword + " OK"
    return generate_dict_response_ok(request, msg, list(parking_zones))

@csrf_exempt
@required_field
def parking_zones_detail(request, zone_id):

    subscriber_uuid = request.POST['subscriber_uuid']
    parking_zone = ParkingZone.objects.filter(id=zone_id).first()

    current_subscription = Subscription.objects.filter(subscriber_uuid=subscriber_uuid, ts__date=date.today(), zone=parking_zone).first()
    if(current_subscription is None):
      if(parking_zone.credit_charge == 0):
        current_subscription = Subscription(subscriber_uuid=subscriber_uuid, zone=parking_zone, credit_charged=0)
        current_subscription.save()

    authorization_status = current_subscription is not None

    parking_spots = []
    if authorization_status:
      parking_spots = ParkingSpot.objects.filter(zone=parking_zone).values()

    tmp = {
      'id': zone_id,
      'authorized': authorization_status,
      'ts_update': parking_zone.ts_update,
      'parking_spots': list(parking_spots),
    }

    print(tmp)
    msg = "Parking Detail OK"
    return generate_dict_response_ok(request, msg, [tmp])

@csrf_exempt
@required_field
def parking_zones_info_all(request):

    subscriber_uuid = request.POST['subscriber_uuid']

    parking_zones = ParkingZone.objects.order_by('id').all()
    list_data = []    
    for zone in parking_zones:
      tmp = get_parking_zone_geopoints(zone, subscriber_uuid)
      list_data.append(tmp)
    msg = "Get All Zones OK"
    return generate_dict_response_ok(request, msg, list_data)

def get_parking_zone_geopoints(zone, subscriber_uuid):

    current_subscription = Subscription.objects.filter(subscriber_uuid=subscriber_uuid, ts__date=date.today(), zone=zone).first()
    if(current_subscription is None):
      if(zone.credit_charge == 0):
        current_subscription = Subscription(subscriber_uuid=subscriber_uuid, zone=zone, credit_charged=0)
        current_subscription.save()

    authorization_status = current_subscription is not None

    parkingzone_geopoints = ParkingZonePolygonGeoPoint.objects.filter(parking_zone=zone).order_by('id').values('id', 'longitude', 'latitude')  
    list_geopoints = list(parkingzone_geopoints)
    tmp = {
      'id': zone.id,
      'authorized': authorization_status,
      'name': zone.name,
      'description': zone.description,
      'center_longitude': zone.center_longitude,
      'center_latitude': zone.center_latitude,
      'credit_charge': zone.credit_charge,
      'ts_update': zone.ts_update,
      'geopoints': list_geopoints
    }
    return tmp

def parking_zones_info_id(request, id):
    parking_zones = ParkingZone.objects.filter(id=id).values('id', 'name', 'description', 'center_longitude', 'center_latitude', 'credit_charge', 'ts_update')
    if parking_zones.count() == 0:
      return generate_dict_response_err(request, 'Zone ID: ' + str(id) + ' Not Found')

    msg = "Get Zone ID: " + str(id) + " OK"
    return generate_dict_response_ok(request, msg, list(parking_zones))

@csrf_exempt
@required_field
def parking_zones_subscribe(request, zone_id):
    subscriber_uuid = request.POST['subscriber_uuid']
    # Assumption: for 1 subscriber, there's only 1 zone subscription for 1 day
    parking_zone = ParkingZone.objects.filter(id=zone_id).first()
    data = Subscription.objects.filter(subscriber_uuid=subscriber_uuid, zone=parking_zone, ts__date=date.today()).first()

    remain_credit = get_remain_credit(subscriber_uuid)
    required_credit = parking_zone.credit_charge

    if(remain_credit < required_credit):
      return generate_dict_response_err(request, 'Credit required: ' + str(required_credit) )

    if data == None:
      data = Subscription(subscriber_uuid=subscriber_uuid, zone=parking_zone, credit_charged=parking_zone.credit_charge)
      data.save()
    msg = "Subscription OK"
    return generate_dict_response_ok(request, msg, [model_to_dict(data)])

def parking_spots_search(request, keyword):
    arr_keyword = keyword.split(" ")
    q_object = Q()
    for word in arr_keyword:
      q_object = q_object & (Q(name__icontains=word)|Q(description__icontains=word))
    parking_zones = ParkingZone.objects.filter(q_object).values('id', 'name', 'description', 'center_longitude', 'center_latitude', 'credit_charge')

    msg = "Search OK"
    return generate_dict_response_ok(request, msg, list(parking_zones))

def generate_dict_response_err(request, msg):
    return {'status': 'ERR', 'path': request.path, 'msg': msg, 'data': []}

def generate_dict_response_ok(request, msg, data):
    return {'status': 'OK', 'path': request.path, 'msg': msg, 'data': data}

# def parking_spots_get_all(request):

  # ts_register = models.DateTimeField(default=now)
  # ts_update = models.DateTimeField(default=now)
  # registrar_uuid = models.CharField(max_length=100)
  # longitude = models.CharField(max_length=100, default="0.0")
  # latitude = models.CharField(max_length=100, default="0.0")
  # voting_available = models.FloatField(default=0)
  # voting_unavailable = models.FloatField(default=0)
  # confidence_level = models.FloatField(default=0)
  # status = models.IntegerField(default=0)
  # zone = models.ForeignKey(ParkingZone, on_delete=models.CASCADE, blank=True, null=True)

#     parking_slots = ParkingSpot.objects.order_by('id').values('id', 'ts_update', 'longitude', 'latitude', 'status', 'confidence_level')
#     return generate_dict_response_ok(request, list(parking_slots))

# def parking_spots_get_id(request, id):
#     parking_spots = ParkingSpot.objects.filter(id=id).values('id', 'ts_update', 'longitude', 'latitude', 'status', 'confidence_level')
#     return generate_dict_response_ok(request, list(parking_spots))

@csrf_exempt
@required_field  
def profile_credit(request):
    subscriber_uuid = request.POST['subscriber_uuid']
    # Assumption: for 1 subscriber, there's only 1 zone subscription for 1 day
    total_credit = get_remain_credit(subscriber_uuid)
    tmp = { 'credit_value' : total_credit, 'subscriber_uuid':  subscriber_uuid}

    msg = "Profile Credit OK"
    return generate_dict_response_ok(request, msg, [tmp])


def get_remain_credit(subscriber_uuid):
    data_participation = ParticipantCredit.objects.filter(participant_uuid=subscriber_uuid).aggregate(Sum('credit_value'))
    total_credit = 0
    if data_participation['credit_value__sum'] is not None:
      total_credit += data_participation['credit_value__sum']

    data_subscription = Subscription.objects.filter(subscriber_uuid=subscriber_uuid).aggregate(Sum('credit_charged'))
    if data_subscription['credit_charged__sum'] is not None:
      total_credit -= data_subscription['credit_charged__sum']
    return total_credit  

@csrf_exempt
@required_field  
def participate_parking_spot(request, status, parking_spot_id):
    subscriber_uuid = request.POST['subscriber_uuid']

    value_participation = 1

    if status == 'unavailable':
      value_participation = -1

    parking_spot = ParkingSpot.objects.filter(id=parking_spot_id).first()
    new_data = ParkingAvailabilityLog(
      participant_uuid = subscriber_uuid,
      longitude = parking_spot.longitude,
      latitude = parking_spot.latitude,
      availability_value = value_participation,
      parking_spot=parking_spot
    )
    new_data.save()

    participation_status, current_time = Participation.participate(
      parking_spot, 
      subscriber_uuid,
      value_participation, 
      DEFAULT_MINUTE_THRESHOLD
    )

    msg = "Participation OK"
    return generate_dict_response_ok(request, msg, [])
