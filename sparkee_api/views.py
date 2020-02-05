from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from sparkee_common.models import ParkingSlot, ParkingAvailabilityLog, ParticipantMovementLog, ParkingAvailabilitySubscription
import json
from django.core import serializers


def summary_all(request):

    cnt_parking_slots = ParkingSlot.objects.distinct('latitude','longitude').count()
    cnt_participants = ParkingAvailabilityLog.objects.distinct('participant_uuid').count()

    send = {
      'participants': cnt_participants,
      'parking_slots': cnt_parking_slots
    }
    return JsonResponse(send, safe=False)


# def parking_slots_near(request, longitude, lattitude):
#     r = float(DEFAULT_RADIUS)
#     lat = float(lattitude)
#     lon = float(longitude)

#     parking_slots = ParkingSlot.objects.filter(
#       longitude__gte = lon-r, 
#       longitude__lte = lon+r, 
#       lattitude__gte = lat-r, 
#       lattitude__lte = lat+r
#     ).values(
#       'id', 
#       'ts_register', 
#       'ts_update', 
#       'longitude', 
#       'lattitude', 
#       'total_available', 
#       'total_unavailable',
#       'status'
#     )
#     return JsonResponse(list(parking_slots), safe=False)

# def summary_near(request, longitude, lattitude):
#     r = float(DEFAULT_RADIUS)
#     lat = float(lattitude)
#     lon = float(longitude)

#     _q = ParkingSlot.objects.filter(
#       longitude__gte = lon-r, 
#       longitude__lte = lon+r, 
#       lattitude__gte = lat-r, 
#       lattitude__lte = lat+r
#     )
#     cnt_parking_slots = _q.distinct('lattitude','longitude').count()

#     _q = ParkingAvailabilityLog.objects.filter(
#       longitude__gte = lon-r, 
#       longitude__lte = lon+r, 
#       lattitude__gte = lat-r, 
#       lattitude__lte = lat+r
#     )
#     cnt_participants = _q.distinct('participant_uuid').count()

#     send = {
#       'participants': cnt_participants,
#       'parking_slots': cnt_parking_slots
#     }
#     return JsonResponse(send, safe=False)


# def subscribe_parking_availability(request, longitude, lattitude, subscriber_uuid):
#     status, current_time = ParkingAvailabilitySubscription.subscribe(DEFAULT_RADIUS, longitude, lattitude, subscriber_uuid)
#     send = {
#       'status': status,
#       'ts': current_time
#     }
#     return JsonResponse(send, safe=False)
