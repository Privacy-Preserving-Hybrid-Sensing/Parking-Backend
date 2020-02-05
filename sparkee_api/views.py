from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from sparkee_common.models import ParkingSlot, DataParticipationParkingAvailability, ParkingZone
import json
from django.core import serializers


def summary_all(request):

    cnt_parking_slots = ParkingSlot.objects.distinct('latitude','longitude').count()
    cnt_participants = DataParticipationParkingAvailability.objects.distinct('participant_uuid').count()
    cnt_parking_zones = ParkingZone.objects.all().count()

    send = {
      'participants': cnt_participants,
      'parking_slots': cnt_parking_slots,
      'parking_zones': cnt_parking_zones
    }
    return JsonResponse(send, safe=False)
