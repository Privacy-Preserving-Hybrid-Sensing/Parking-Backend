from background_task import background
from logging import getLogger
import pika
import json
from sparkee_common.models import ParkingAvailabilityLog, ParticipantMovementLog, ParkingSlot, ParkingAvailabilitySubscription
from datetime import datetime, timedelta
from django.conf import settings
import threading
import os
import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


env = environ.Env()
environ.Env.read_env(BASE_DIR + "/.env")  # reading .env file

DEFAULT_RADIUS = 0.01

class AMQPConsuming(threading.Thread):
    # connection = None
    # from sparkee_common.models import ParkingAvailabilityLog, ParticipantMovementLog, ParkingSlot

    def callback_mobile_activity(self, ch, method, properties, body):
      json_data = json.loads(body)
      print(json_data)

      if json_data['type'] == 'parking_slot_registration':
        default_parking_status = "Unavailable"
        new_data = ParkingSlot(
          participant_uuid = json_data['routing_key_uuid'],
          longitude = json_data['long'],
          lattitude = json_data['latt'],
          confidence_available = 0,
          confidence_unavailable = 0
        )
        new_data.save()
        submit_background_job_parking_availability()
      elif json_data['type'] == 'parking_availability':
        # default value: available

        value_participation = 1
        if json_data['msg'] == 'Unavailable':
          value_participation = -1

        new_data = ParkingAvailabilityLog(
          participant_uuid = json_data['routing_key_uuid'],
          longitude = json_data['long'],
          lattitude = json_data['latt'],
          value = value_participation
        )
        new_data.save()
        submit_background_job_parking_availability()

      elif json_data['type'] == 'participant_location':
        value_participation = 0
        new_data = ParticipantMovementLog(
          participant_uuid = json_data['routing_key_uuid'],
          longitude = json_data['long'],
          lattitude = json_data['latt']
        )
        new_data.save()

        status, current_time = ParkingAvailabilitySubscription.subscribe(DEFAULT_RADIUS, json_data['long'], json_data['latt'], json_data['routing_key_uuid'])

    def run(self):
        # connection = self._get_connection()
        # print(self.connection)
        channel = connection.channel()
        channel.exchange_declare(exchange='DEVICE_TO_SERVER', exchange_type='fanout', auto_delete=True)

        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='DEVICE_TO_SERVER', queue=queue_name)

        print(' [*] Waiting for SParkeeMobile report. To exit press CTRL+C')


        channel.basic_consume(queue=queue_name, on_message_callback=self.callback_mobile_activity, auto_ack=True)
        channel.start_consuming()

credentials = pika.PlainCredentials(env('RABBITUSER'), env('RABBITPASS'))
parameters = pika.ConnectionParameters(
    env('RABBITHOST'),
    env('RABBITPORT'),
    env('RABBITVHOST'),
    credentials
)

connection = pika.BlockingConnection(parameters)

consumer = AMQPConsuming()
consumer.connection = connection
consumer.daemon = True
consumer.start()      


@background(queue="background_job_parking_availability")
def submit_background_job_parking_availability():
    current_time = datetime.now()
    print(current_time)
    calculate_availability()

def calculate_availability():
    time_treshold = datetime.now() - timedelta(minutes=5)
    data_treshold = ParkingAvailabilityLog.objects.filter(ts__gt=time_treshold).all().values_list()
    for data in data_treshold:
      print(data)
    