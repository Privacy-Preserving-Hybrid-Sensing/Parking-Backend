from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg, Max, Min, Sum
from django.db.models import Q
from backend.models import ParkingSpot, Participation, ParkingZone, ParkingZonePolygonGeoPoint, Subscription, ParkingAvailabilityLog, Profile, History
import json, requests
from django.core import serializers
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, date
from .decorators import required_field

DEFAULT_MINUTE_THRESHOLD = 5
BASE_VALIDATION = "http://localhost:8000/web/validation/"

# ZK
ZK_HOST = "http://localhost:8080/"
ZK_URL_CRYPTO_INFO = ZK_HOST + "getCryptoInfo"
ZK_URL_REGISTER = ZK_HOST + "register"
ZK_URL_DATA_SUBMISSION = ZK_HOST + "submitData"
ZK_URL_VERIFY_CREDENTIAL = ZK_HOST + "claimVerifyCredential"
ZK_URL_VERIFY_Q = ZK_HOST + "claimVerifyQ"
ZK_URL_CLAIM_REWARD = ZK_HOST + "claimReward"

@csrf_exempt
@required_field
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

@csrf_exempt
@required_field
def zones_search_keyword(request, keyword):
    arr_keyword = keyword.split(" ")
    q_object = Q()
    for word in arr_keyword:
      q_object = q_object & (Q(name__icontains=word)|Q(description__icontains=word))
    parking_zones = ParkingZone.objects.filter(q_object).values('id', 'name', 'description', 'center_longitude', 'center_latitude', 'credit_required')
    msg = "Search " + keyword + " OK"
    return generate_dict_response_ok(request, msg, list(parking_zones))

@csrf_exempt
@required_field
def zones_id(request, zone_id):

    subscriber_uuid = request.headers['Subscriber-Uuid']

    zone = ParkingZone.objects.filter(id=zone_id).first()
    if zone is None:
      msg = "Parking Zone ID: " + str(zone_id) + " Not Found"
      return generate_dict_response_err(request, msg)

    tmp = get_parking_zone_geopoints(zone, subscriber_uuid)
    msg = "Get Zone " + str(zone_id) + " OK"
    return generate_dict_response_ok(request, msg, tmp)

@csrf_exempt
@required_field
def zones_all(request):

    subscriber_uuid = request.headers['Subscriber-Uuid']

    parking_zones = ParkingZone.objects.order_by('id').all()
    list_data = []    
    for zone in parking_zones:
      tmp = get_parking_zone_geopoints(zone, subscriber_uuid)
      list_data.append(tmp)
    msg = "Get All Zones OK"
    return generate_dict_response_ok(request, msg, list_data)

def get_parking_zone_geopoints(zone, subscriber_uuid):

    current_subscription = Subscription.objects.filter(subscriber_uuid=subscriber_uuid, ts_subscription__date=date.today(), zone=zone).first()
    if(current_subscription is None):
      if(zone.credit_required == 0):
        current_subscription = Subscription.subscribe(subscriber_uuid=subscriber_uuid, zone=zone, charged=0)

    subscription_status = current_subscription is not None

    parkingzone_geopoints = ParkingZonePolygonGeoPoint.objects.filter(parking_zone=zone).order_by('id').values('id', 'longitude', 'latitude')  

    cnt_available = -1
    cnt_unavailable = -1
    cnt_undefined = -1
    cnt_total = -1

    subscription_token = ""
    if subscription_status:
      cnt_available = ParkingSpot.objects.filter(zone=zone, parking_status__gt=0).count()
      cnt_unavailable = ParkingSpot.objects.filter(zone=zone, parking_status__lt=0).count()
      cnt_undefined = ParkingSpot.objects.filter(zone=zone, parking_status=0).count()
      cnt_total = cnt_available + cnt_unavailable + cnt_undefined
      subscription_token = zone.token


    list_geopoints = list(parkingzone_geopoints)
    tmp = {
      'id': zone.id,
      'subscribed': subscription_status,
      'subscription_token': subscription_token,
      'name': zone.name,
      'description': zone.description,
      'center_longitude': zone.center_longitude,
      'center_latitude': zone.center_latitude,
      'credit_required': zone.credit_required,
      'ts_update': zone.ts_update,
      'spot_total': cnt_total,
      'spot_available': cnt_available,
      'spot_unavailable': cnt_unavailable,
      'spot_undefined': cnt_undefined,
      'geopoints': list_geopoints
    }
    return tmp

@csrf_exempt
@required_field
def zones_id_spots_all(request, zone_id):
    parking_zone = ParkingZone.objects.filter(id=zone_id).first()
    
    if parking_zone is None:
      return generate_dict_response_err(request, 'Zone ID: ' + str(zone_id) + ' Not Found')

    subscriber_uuid = request.headers['Subscriber-Uuid']
    current_subscription = Subscription.objects.filter(subscriber_uuid=subscriber_uuid, ts_subscription__date=date.today(), zone=parking_zone.id).first()

    if current_subscription is None:
      return generate_dict_response_err(request, 'Requires ' + str(parking_zone.credit_required) + " Credit to subscribe to " + parking_zone.name)

    parking_spots = ParkingSpot.objects.filter(zone=parking_zone).all()
    ret = []
    for parking_spot in parking_spots:
      tmp = {
        "id": parking_spot.id, 
        "name": parking_spot.name, 
        "ts_register": parking_spot.ts_register,
        "ts_update": parking_spot.ts_update,
        "registrar_uuid": parking_spot.registrar_uuid,
        "longitude": parking_spot.longitude,
        "latitude": parking_spot.latitude,
        "vote_available": parking_spot.vote_available,
        "vote_unavailable": parking_spot.vote_unavailable,
        "confidence_level": parking_spot.confidence_level,
        "parking_status": parking_spot.parking_status,
        "zone_id": parking_spot.zone.id
      }
      ret.append(tmp)
    
    msg = "Get All Parking Spots in Zone ID: " + str(zone_id) + " OK"
    return generate_dict_response_ok(request, msg, ret)

@csrf_exempt
@required_field
def zones_id_spots_id(request, zone_id, spot_id):
    parking_zone = ParkingZone.objects.filter(id=zone_id).first()
    
    if parking_zone is None:
      msg = "Parking Zone ID: " + str(zone_id) + " Not Found"
      return generate_dict_response_err(request, msg)

    parking_spot = ParkingSpot.objects.filter(zone=parking_zone, id=spot_id).first()

    if parking_spot is None:
      msg = "Parking Spot ID: " + str(spot_id) + " in Zone ID: " + str(zone_id) + " Not Found"
      return generate_dict_response_err(request, msg)

    ret = {
        "id": parking_spot.id, 
        "name": parking_spot.name, 
        "ts_register": parking_spot.ts_register,
        "ts_update": parking_spot.ts_update,
        "registrar_uuid": parking_spot.registrar_uuid,
        "longitude": parking_spot.longitude,
        "latitude": parking_spot.latitude,
        "vote_available": parking_spot.vote_available,
        "vote_unavailable": parking_spot.vote_unavailable,
        "confidence_level": parking_spot.confidence_level,
        "parking_status": parking_spot.parking_status,
        "zone_id": parking_spot.zone.id
    }
    
    msg = "Get Parking Spot ID: " + str(spot_id) + " in Zone ID: " + str(zone_id) + " OK"
    return generate_dict_response_ok(request, msg, ret)

@csrf_exempt
@required_field
def zones_id_subscribe(request, zone_id):
    subscriber_uuid = request.headers['Subscriber-Uuid']
    # Assumption: for 1 subscriber, there's only 1 zone subscription for 1 day
    parking_zone = ParkingZone.objects.filter(id=zone_id).first()
    if parking_zone is None:
      msg = "Parking Zone ID: " + str(zone_id) + " Not Found"
      return generate_dict_response_err(request, msg)

    subscription = Subscription.objects.filter(subscriber_uuid=subscriber_uuid, zone=parking_zone, ts_subscription__date=date.today()).first()

    incentive = get_incentive(subscriber_uuid)
    charged = get_charged(subscriber_uuid)

    balance = incentive - charged

    required_credit = parking_zone.credit_required

    if(balance < required_credit):
      return generate_dict_response_err(request, 'Credit required: ' + str(required_credit) + ", subscriber_uuid: " + subscriber_uuid + " only have " + str(balance) )

    msg = ""
    if subscription is not None:
      msg = "Parking Zone ID: " + str(zone_id) + " already subscribed today"

    if subscription == None:
      msg = "Subscription OK"
      subscription = Subscription.subscribe(subscriber_uuid=subscriber_uuid, zone=parking_zone, charged=parking_zone.credit_required)

    ret = {
      "id": subscription.id,
      "ts_subscription": subscription.ts_subscription,
      "subscriber_uuid": subscription.subscriber_uuid,
      "subscription_token": parking_zone.token,
      "zone_id": subscription.zone.id,
      "charged": subscription.charged
    }

    return generate_dict_response_ok(request, msg, ret)

@csrf_exempt
@required_field
def parking_spots_search(request, keyword):
    arr_keyword = keyword.split(" ")
    q_object = Q()
    for word in arr_keyword:
      q_object = q_object & (Q(name__icontains=word)|Q(description__icontains=word))
    parking_zones = ParkingZone.objects.filter(q_object).values('id', 'name', 'description', 'center_longitude', 'center_latitude', 'credit_required')

    msg = "Search OK"
    return generate_dict_response_ok(request, msg, list(parking_zones))

def generate_dict_response_err(request, msg):
    return {'status': 'ERR', 'path': request.path, 'msg': msg, 'data': []}

def generate_dict_response_ok(request, msg, data):
    return {'status': 'OK', 'path': request.path, 'msg': msg, 'data': data}


@csrf_exempt
@required_field  
def profile_summary(request):
    subscriber_uuid = request.headers['Subscriber-Uuid']
    # Assumption: for 1 subscriber, there's only 1 zone subscription for 1 day
    participation = get_participation(subscriber_uuid)
    incentive = get_incentive(subscriber_uuid)
    charged = get_charged(subscriber_uuid)

    balance = incentive - charged
    tmp = { 'participation': participation, 'balance' : balance, 'incentive': incentive, 'charged': charged}

    msg = "Profile Credit OK"
    return generate_dict_response_ok(request, msg, tmp)

def get_participation(subscriber_uuid):
    cnt_participation = Participation.objects.filter(participant_uuid=subscriber_uuid).count()
    return cnt_participation

def get_dummy_parking_spot():
    spot = ParkingSpot.objects.filter(name='Free Credits').first()
    if spot is None:
        zone = ParkingZone.objects.filter(name="Free Credits").first()
        if zone is None:
            zone = ParkingZone(name="Free Credit", credit_required=0)
            zone.save()
        spot = ParkingSpot(name="Free Credits", zone=zone)
        spot.save()
    return spot

def get_incentive(subscriber_uuid):
    participant_cnt = Participation.objects.filter(participant_uuid=subscriber_uuid).count()
    if participant_cnt == 0:
        dummy_spot = get_dummy_parking_spot()
        free_credit = Participation(participant_uuid=subscriber_uuid, parking_spot=dummy_spot, incentive_processed=True, participation_value=0, incentive_value=100)
        free_credit.save()
        history = History(subscriber_uuid=subscriber_uuid, participation=free_credit )
        history.save()

    data_participation = Participation.objects.filter(participant_uuid=subscriber_uuid, incentive_processed=True).aggregate(Sum('incentive_value'))
    incentive = 0
    if data_participation['incentive_value__sum'] is not None:
      incentive += data_participation['incentive_value__sum']
    return incentive

def get_charged(subscriber_uuid):
    data_charged = Subscription.objects.filter(subscriber_uuid=subscriber_uuid).aggregate(Sum('charged'))
    charged = 0
    if data_charged['charged__sum'] is not None:
      charged += data_charged['charged__sum']
    return charged

def get_remain_credit(subscriber_uuid):
    data_participation = Participation.objects.filter(participant_uuid=subscriber_uuid, incentive_processed=True).aggregate(Sum('incentive_value'))
    total_credit = 0
    if data_participation['incentive_value__sum'] is not None:
      total_credit += data_participation['incentive_value__sum']

    data_subscription = Subscription.objects.filter(subscriber_uuid=subscriber_uuid).aggregate(Sum('charged'))
    if data_subscription['charged__sum'] is not None:
      total_credit -= data_subscription['charged__sum']
    return total_credit  

@csrf_exempt
@required_field  
def participate_zone_spot_status(request, zone_id, spot_id, str_status):
    subscriber_uuid = request.headers['Subscriber-Uuid']

    value_participation = 1
    if str_status == 'unavailable':
      value_participation = -1

    parking_zone = ParkingZone.objects.filter(id=zone_id).first()

    parking_spot = ParkingSpot.objects.filter(id=spot_id, zone=parking_zone).first()

    data = Participation.participate(
      parking_spot, 
      subscriber_uuid,
      value_participation, 
      DEFAULT_MINUTE_THRESHOLD
    )


    tmp = {
      'id': data.id,
      'ts_create': data.ts_create,
      'ts_update': data.ts_update,
      'zone_id': data.parking_spot.zone.id,
      'zone_name': data.parking_spot.zone.name,
      'spot_id': data.parking_spot.id,
      'spot_name': data.parking_spot.name,
      'previous_value': data.previous_value,
      'participation_value': data.participation_value,
      'incentive_value': data.incentive_value,
      'incentive_processed': data.incentive_processed
    }

    msg = "Participation OK"
    return generate_dict_response_ok(request, msg, tmp)


@csrf_exempt
@required_field  
def profile_participations_latest(request):
    subscriber_uuid = request.headers['Subscriber-Uuid']
    # Assumption: for 1 subscriber, there's only 1 zone subscription for 1 day
    time_treshold = datetime.now() - timedelta(minutes=DEFAULT_MINUTE_THRESHOLD)

    participant_datas = Participation.objects.filter(participant_uuid=subscriber_uuid, ts_create__gt=time_treshold).order_by('ts_create').all()
    ret = []
    for data in participant_datas:
      tmp = {
        'id': data.id,
        'ts_create': data.ts_create,
        'ts_update': data.ts_update,
        'zone_id': data.parking_spot.zone.id,
        'zone_name': data.parking_spot.zone.name,
        'spot_id': data.parking_spot.id,
        'spot_name': data.parking_spot.name,
        'previous_value': data.previous_value,
        'participation_value': data.participation_value,
        'incentive_value': data.incentive_value,
        'incentive_processed': data.incentive_processed
      }
      ret.append(tmp)

    msg = "Latest Participations OK"
    return generate_dict_response_ok(request, msg, ret)


@csrf_exempt
@required_field  
def profile_participations_last_num_participation(request, last_num_participation):
    subscriber_uuid = request.headers['Subscriber-Uuid']
    # Assumption: for 1 subscriber, there's only 1 zone subscription for 1 day

    participant_datas = Participation.objects.filter(participant_uuid=subscriber_uuid).order_by('-ts_create').all()[:last_num_participation]
    ret = []
    for data in participant_datas:
      tmp = {
        'id': data.id,
        'ts_create': data.ts_create,
        'ts_update': data.ts_update,
        'zone_id': data.parking_spot.zone.id,
        'zone_name': data.parking_spot.zone.name,
        'spot_id': data.parking_spot.id,
        'spot_name': data.parking_spot.name,
        'previous_value': data.previous_value,
        'participation_value': data.participation_value,
        'incentive_value': data.incentive_value,
        'incentive_processed': data.incentive_processed
      }
      ret.append(tmp)

    msg = "Participation cnt " + str(last_num_participation) + " OK"
    return generate_dict_response_ok(request, msg, ret)

@csrf_exempt
@required_field  
def profile_register_email(request, email):
    subscriber_uuid = request.headers['Subscriber-Uuid']
    # Assumption: for 1 subscriber, there's only 1 zone subscription for 1 day
    profile = Profile.register(subscriber_uuid=subscriber_uuid, email=email)
    validation_url = BASE_VALIDATION + profile.key_validation
    msg = "Profile Register OK"
    tmp = {
      "id": profile.id,
      "ts": profile.ts,
      "subscriber_uuid": profile.subscriber_uuid,
      "email": profile.email,
      "validation_url": validation_url,
      "validated": profile.validated
    }
    return generate_dict_response_ok(request, msg, [tmp])


@csrf_exempt
@required_field  
def profile_history_last_num_history(request, last_num_history):
    subscriber_uuid = request.headers['Subscriber-Uuid']
    # Assumption: for 1 subscriber, there's only 1 zone subscription for 1 day

    history_data = History.objects.filter(subscriber_uuid=subscriber_uuid).order_by('ts_history').all()
    ret = []
    balance = 0
    for data in history_data:
      if data.participation is not None:
        participant_data = Participation.objects.filter(id=data.participation.id).first()
        balance += participant_data.incentive_value
        tmp = {
          'id_history': data.id,
          'id_participation': participant_data.id,
          'type': 'participation',
          'ts_create': participant_data.ts_create,
          'ts_update': participant_data.ts_update,
          'zone_id': participant_data.parking_spot.zone.id,
          'zone_name': participant_data.parking_spot.zone.name,
          'spot_id': participant_data.parking_spot.id,
          'spot_name': participant_data.parking_spot.name,
          'previous_value': participant_data.previous_value,
          'participation_value': participant_data.participation_value,
          'incentive_value': participant_data.incentive_value,
          'incentive_processed': participant_data.incentive_processed,
          'balance': balance
        }
        ret.append(tmp)

      elif data.subscription is not None:
        subscription_data = Subscription.objects.filter(id=data.subscription.id, charged__gt=0).first()
        if subscription_data is not None:
          balance -= subscription_data.charged
          tmp = {
            'id_history': data.id,
            'id_subscription': subscription_data.id,
            'type': 'subscription',
            'ts_subscription': subscription_data.ts_subscription,
            'zone_id': subscription_data.zone.id,
            'zone_name': subscription_data.zone.name,
            'charged': subscription_data.charged,
            'balance': balance
          }
          ret.append(tmp)

    msg = "History cnt " + str(last_num_history) + " OK"
    reverse = ret[::-1]

    return generate_dict_response_ok(request, msg, reverse[:last_num_history])


#### ZK IMPLEMENTATION ####
def generate_zk_response_err(request, msg):
    return {'status': 'ERR', 'path': request.path, 'msg': msg, 'zk': []}

def generate_zk_response_ok(request, msg, data):
    return {'status': 'OK', 'path': request.path, 'msg': msg, 'zk': data}

def zk_post(url, json):
    headers = {"Content-Type":"application/json"}
    return requests.post(url, json=json, headers=headers)

@csrf_exempt
@required_field  
def zk_serve_crypto_info(request):
    # TODO: TANYA PAK ADIN, INI HEADER YANG UUID SAMA 1 LAGI BUAT APA DI BACKEND?
    message = "ZK Crypto info service"
    response = requests.get(ZK_URL_CRYPTO_INFO)
    return generate_zk_response_ok(request, message, response)

@csrf_exempt
@required_field  
def zk_register(request):
    # TODO: TANYA PAK ADIN, INI HEADER YANG UUID SAMA 1 LAGI BUAT APA DI BACKEND?
    message = "ZK Registration service"
    response = zk_post(ZK_URL_REGISTER, json.loads(request.body.decode('utf-8')))
    return generate_zk_response_ok(request, message, response)