from background_task import background
from django.core.serializers.json import DjangoJSONEncoder
from logging import getLogger
import pika
import json
from sparkee_common.models import ParkingAvailabilityLog, ParticipantMovementLog, ParkingSlot, ParkingAvailabilitySubscription, ParkingZone, ParticipantCredit, DataParticipationParkingAvailability
from datetime import datetime, timedelta, date
from django.conf import settings
import threading
import os
import environ
import time
from django.db.models.functions import Cast
from django.db.models import TextField

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


env = environ.Env()
environ.Env.read_env(BASE_DIR + "/.env")  # reading .env file

DEFAULT_MINUTE_THRESHOLD = 1
DEFAULT_PARTICIPANT_TO_SERVER_ROUTING_KEY = "PARTICIPANT_TO_SERVER"

credentials = pika.PlainCredentials(env('RABBITUSER'), env('RABBITPASS'))
parameters = pika.ConnectionParameters(
    env('RABBITHOST'),
    env('RABBITPORT'),
    env('RABBITVHOST'),
    credentials
)

connection_send = pika.BlockingConnection(parameters)
channel_send = connection_send.channel()

connection_recv = pika.BlockingConnection(parameters)
channel_recv = connection_recv.channel()
queue_name_recv = channel_recv.queue_declare('', exclusive=True).method.queue
channel_recv.queue_bind(exchange="amq.topic", routing_key=DEFAULT_PARTICIPANT_TO_SERVER_ROUTING_KEY, queue=queue_name_recv)

class MAJORITY_Thread(threading.Thread):
    channel = None

    def calculate_parking_log(self):
        time_treshold = datetime.now() - timedelta(minutes=DEFAULT_MINUTE_THRESHOLD)
        parking_changed_logs = DataParticipationParkingAvailability.objects.filter(ts_update__gt=time_treshold).all()
        data = {}

        # TODO: Get the data using Postgres/Django models Query
        for parking_data in parking_changed_logs:
          id_data = parking_data.id
          availability_value = parking_data.availability_value
          if id_data not in data:
            data[id_data] = { 'available': 0, 'unavailable': 0, 'total_participants': 0, 'longitude': parking_data.longitude, 'latitude': parking_data.latitude}

          if availability_value < 0:
            data[id_data]['unavailable'] += 1
          elif availability_value > 0:
            data[id_data]['available'] += 1
          data[id_data]['total_participants'] += 1

        for parking_slot_id in list(data):
          self.decide_parking_status(data[parking_slot_id])

    def decide_parking_status(self, data):
        delta = data['available'] - data['unavailable']
        total = data['total_participants']
        confidence_level = 0
        parking_status = 0
        if delta > 0:
          confidence_level = data['available'] / total
          if confidence_level > 0.7:
            parking_status = 3
          elif confidence_level > 0.4:
            parking_status = 2
          else:
            parking_status = 1

        elif delta < 0:
          confidence_level = data['unavailable'] / total
          if confidence_level > 0.7:
            parking_status = -3
          elif confidence_level > 0.4:
            parking_status = -2
          else:
            parking_status = -1
        ParkingSlot.change(data['longitude'], data['latitude'], data['available'], data['unavailable'], parking_status, confidence_level)


        # calculate_majority_last_five_minutes()
        # calculate_unavailability()
        # calculate_status()

    def run(self):
        while True:
          self.calculate_parking_log()
          time.sleep(30)
          # Check every 30 seconds interval to get majority score

class AMQP_Publish_Time_Thread(threading.Thread):
    channel = None
    def run(self):
        while True:
          message = datetime.now().strftime("%c")
          try:
            self.channel.basic_publish(exchange='amq.topic', routing_key='time', body=message)
          except:
            print("Some Publish Error, skip this Time loop process")
          
          time.sleep(1)

class AMQP_Publish_Parking_zone_thread(threading.Thread):
    channel = None
    def run(self):
        while True:
          time_treshold = datetime.now() - timedelta(minutes=DEFAULT_MINUTE_THRESHOLD)
          parking_zones = ParkingZone.objects.all()
          try:
            for parking_zone in parking_zones:
              # print(parking_zone)
              publish_parkingslots_by_parkingzone(parking_zone)

          except:
            print("Some Publish Error, skip this Parking Zone loop process")

          time.sleep(10)
        

class AMQP_Consumer_Thread(threading.Thread):
    channel = None
    queue_name = ""
    def callback_mobile_activity(self, ch, method, properties, body):
      json_data = json.loads(body)
      # print(json_data)

      if json_data['action'] == 'parking_slot_registration':
        # TODO: This is just for Admin only
        zone = ParkingZone.objects.filter(name='All Zones').first()
        ParkingSlot.create(
          registrar_uuid = json_data['device_uuid'],
          longitude = json_data['lon'],
          latitude = json_data['lat'],
          zone = zone
        )

      elif json_data['action'] == 'parking_availability':
        # default value: available
        self.process_participation(json_data)
        publish_participation_by_device_uuid(json_data['device_uuid'])

      elif json_data['action'] == 'participant_location':
        data_movement = ParticipantMovementLog(
          participant_uuid = json_data['device_uuid'],
          longitude = json_data['lon'],
          latitude = json_data['lat']
        )
        data_movement.save()
        
        ParkingAvailabilitySubscription.subscribe(
          longitude=json_data['lon'], 
          latitude=json_data['lat'], 
          subscriber_uuid=json_data['device_uuid'],
          subscriber_type=json_data['device_type']
        )

      publish_participation_by_device_uuid(json_data['device_uuid'])

    def process_participation(self, json_data):
        
        value_participation = 1

        if json_data['msg'] == 'Unavailable':
          value_participation = -1

        new_data = ParkingAvailabilityLog(
          participant_uuid = json_data['device_uuid'],
          longitude = json_data['lon'],
          latitude = json_data['lat'],
          availability_value = value_participation
        )
        new_data.save()

        participation_status, current_time = DataParticipationParkingAvailability.participate(
          json_data['lon'], 
          json_data['lat'], 
          json_data['device_uuid'], 
          value_participation, 
          DEFAULT_MINUTE_THRESHOLD
        )

    def run(self):
        print(' [*] Waiting for SParkeeMobile report. To exit press CTRL+C')

        self.channel.basic_consume(on_message_callback=self.callback_mobile_activity, auto_ack=True, queue=self.queue_name)
        self.channel.start_consuming()


consumer_thread = AMQP_Consumer_Thread()
consumer_thread.channel = channel_recv
consumer_thread.queue_name = queue_name_recv
consumer_thread.daemon = True
consumer_thread.start()      


publish_time_thread = AMQP_Publish_Time_Thread()
publish_time_thread.channel = channel_send
publish_time_thread.daemon = True
publish_time_thread.start()      


publish_parking_zone_thread = AMQP_Publish_Parking_zone_thread()
publish_parking_zone_thread.channel = channel_send
publish_parking_zone_thread.daemon = True
publish_parking_zone_thread.start()      


majority_thread = MAJORITY_Thread()
majority_thread.daemon = True
majority_thread.start()

@background(queue="submit_background_job")
def submit_background_job():
    current_time = datetime.now()

def publish_participation_by_device_uuid(device_uuid):
    time_treshold = datetime.now() - timedelta(minutes=DEFAULT_MINUTE_THRESHOLD)
    participant_credits = ParticipantCredit.objects.filter(ts_update__gt=time_treshold, participant_uuid=device_uuid).all()
    topic = "participant." + device_uuid
    payload_type = "participant_credits"
    send_participant_credits_to_topic(topic, participant_credits, payload_type)

def publish_parkingslots_by_parkingzone(parking_zone):
    parking_slots = ParkingSlot.objects.filter(zone=parking_zone).all()
    topic = "zone." + str(parking_zone.id)
    payload_type = "parking_slots"
    send_parking_slots_to_topic(topic, parking_slots, payload_type)

def send_participant_credits_to_topic(amqp_topic, participant_credits, payload_type):
    list_msg = []

    for credit in participant_credits:
      tmp = {
        'id_participation': credit.participation.id,
        'id_credit': credit.id,
        'ts_participation': credit.participation.ts_update.isoformat(),
        'ts_credit': credit.ts_update.isoformat(),
        'longitude': credit.participation.longitude,
        'latitude': credit.participation.latitude,
        'availability_value': credit.participation.availability_value,
        'credit_value': credit.credit_value,
        'participation_processed': credit.participation.processed,
        'credit_processed': credit.processed
      }
      list_msg.append(tmp)

    send_data = {
      'type': payload_type,
      'payload': list_msg
    }

    message = json.dumps(send_data, cls=DjangoJSONEncoder)
    send_to_topic(amqp_topic, message, payload_type)
    # print(message)


def send_parking_slots_to_topic(amqp_topic, parking_slots, payload_type):
    list_msg = []

    for slot in parking_slots:
      tmp = {
        'id': slot.id,
        'ts_register': slot.ts_register.isoformat(),
        'ts_update': slot.ts_update.isoformat(),
        'longitude': slot.longitude,
        'latitude': slot.latitude,
        'total_available': slot.total_available,
        'total_unavailable': slot.total_unavailable,
        'confidence_level' : slot.confidence_level,
        'status': slot.status,
        'zone_id': slot.zone.id,
        'zone_name': slot.zone.name
      }
      list_msg.append(tmp)

    send_data = {
      'type': payload_type,
      'payload': list_msg
    }

    # print(send_data)
    message = json.dumps(send_data, cls=DjangoJSONEncoder)
    send_to_topic(amqp_topic, message, payload_type)

def send_to_topic(amqp_topic, message, payload_type):
    try:
      current_time = datetime.now()

      channel_send.basic_publish(exchange='amq.topic', routing_key=amqp_topic, body=message)
      # print(current_time.strftime("%Y-%m-%d, %H:%M:%S") + " -- Publish to Topic: " + amqp_topic + ", Payload Type: "+ payload_type )
    except:
      print("Some Publish Error, skip this send process")
