from background_task import background
from django.core.serializers.json import DjangoJSONEncoder
from logging import getLogger
import pika
import json
from backend.models import ParkingAvailabilityLog, ParticipantMovementLog, ParkingSpot, Subscription, ParkingZone, Participation, ParkingZonePolygonGeoPoint, ParkingSpotHistory
from datetime import datetime, timedelta, date
from django.conf import settings
import threading
import os
import environ
import time
from django.db.models.functions import Cast
from django.db.models import TextField
from .amqppublisher import AMQPPublisher

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


env = environ.Env()
environ.Env.read_env(BASE_DIR + "/.env")  # reading .env file

PROCESSING_TIME_WINDOW = 300    # IN SECONDS (300 seconds => 5 minutes)
PROCESSING_INTERVAL = 3        # IN SECONDS


# DEFAULT_PARTICIPANT_TO_SERVER_ROUTING_KEY = "PARTICIPANT_TO_SERVER"

credentials = pika.PlainCredentials(env('RABBITUSER'), env('RABBITPASS'))
parameters = pika.ConnectionParameters(
    env('RABBITHOST'),
    env('RABBITPORT'),
    env('RABBITVHOST'),
    credentials
)


# connection_recv = pika.BlockingConnection(parameters)
# channel_recv = connection_recv.channel()
# queue_name_recv = channel_recv.queue_declare('', exclusive=True).method.queue
# channel_recv.queue_bind(exchange="amq.topic", routing_key=DEFAULT_PARTICIPANT_TO_SERVER_ROUTING_KEY, queue=queue_name_recv)

# amqp_url = 'amqp://'+ env('RABBITUSER') +':'+ env('RABBITPASS') +'@'+ env('RABBITHOST') +':'+ env('RABBITPORT') +'/%2F?connection_attempts=30&heartbeat=3600'
# publisher = AMQPPublisher(amqp_url)
# publisher.run()
# publisher.publish_message("TES123")


class MAJORITY_Thread(threading.Thread):
    channel = None

    def calculate_parking_log(self):
        data_collected = self.collect_data_inside_time_window()
        self.decide_parking_status(data_collected)

    def collect_data_inside_time_window(self):
        time_window_ev = datetime.now() - timedelta(seconds=PROCESSING_TIME_WINDOW + PROCESSING_INTERVAL)
        data = {}

        participation_activity_logs = Participation.objects.filter(ts_update__gt=time_window_ev).all()
        for participation_activity in participation_activity_logs:
          spot_id = participation_activity.parking_spot.id
          data[spot_id] = { 'spot_id': spot_id, 'available': 0, 'unavailable': 0, 'total_participants': 0}
        print(data)

        time_window_tr = datetime.now() - timedelta(seconds=PROCESSING_TIME_WINDOW)
        participation_in_treshold_logs = Participation.objects.filter(ts_update__gt=time_window_tr).all()
        for participation_in_treshold in participation_in_treshold_logs:
          spot_id = participation_in_treshold.parking_spot.id
          availability_value = participation_in_treshold.participation_value

          if availability_value < 0:
            data[spot_id]['unavailable'] += 1
          elif availability_value > 0:
            data[spot_id]['available'] += 1
          data[spot_id]['total_participants'] += 1

        print(data)
        return data

    def decide_parking_status(self, data_collected):
        for spot_id in data_collected:
          data = data_collected[spot_id]
          majority = data['available'] - data['unavailable']
          total = data['total_participants']
          confidence_level = 1
          parking_status = 0

          if total > 0:
            if majority > 0:
              confidence_level = data['available'] / total
              if confidence_level > 0.7:
                parking_status = 3
              elif confidence_level > 0.4:
                parking_status = 2
              elif confidence_level > 0.1:
                parking_status = 1

            elif majority < 0:
              confidence_level = data['unavailable'] / total
              if confidence_level > 0.7:
                parking_status = -3
              elif confidence_level > 0.4:
                parking_status = -2
              elif confidence_level > 0.1:
                parking_status = -1

          current_parking_spot_data = ParkingSpot.objects.filter(id=data['spot_id']).first()
          if current_parking_spot_data.parking_status != parking_status:
            ts_latest = datetime.now()

            history = ParkingSpotHistory(
              name = current_parking_spot_data.name,
              ts_previous = current_parking_spot_data.ts_update,
              ts_latest = ts_latest,
              registrar_uuid = current_parking_spot_data.registrar_uuid,
              longitude = current_parking_spot_data.longitude,
              latitude = current_parking_spot_data.latitude,
              vote_available = data['available'],
              vote_unavailable = data['unavailable'],
              confidence_level = confidence_level,
              parking_status = parking_status,
              parking_spot = current_parking_spot_data,
              zone = current_parking_spot_data.zone
            )
            history.save()

            current_parking_spot_data.vote_available = data['available']
            current_parking_spot_data.vote_unavailable = data['unavailable']
            current_parking_spot_data.confidence_level = confidence_level
            current_parking_spot_data.parking_status = parking_status
            current_parking_spot_data.ts_update = ts_latest
            current_parking_spot_data.save()

          self.broadcast_parking_spot_changes_with_topic_zone_token(current_parking_spot_data)

    def broadcast_parking_spot_changes_with_topic_zone_token(self, parking_spot):
        token = parking_spot.zone.token
        tmp = {  
          "status": "OK", 
          "path": "/api/zones/"+  str(parking_spot.zone.id)  +"/spots/" + str(parking_spot.id), 
          "msg": "Broadcast OK", 
          "data": {
            "id": parking_spot.id, 
            "name": parking_spot.name, 
            "ts_register": parking_spot.ts_register.isoformat(),
            "ts_update": parking_spot.ts_update.isoformat(),
            "registrar_uuid": parking_spot.registrar_uuid,
            "longitude": parking_spot.longitude,
            "latitude": parking_spot.latitude,
            "vote_available": parking_spot.vote_available,
            "vote_unavailable": parking_spot.vote_unavailable,
            "confidence_level": parking_spot.confidence_level,
            "parking_status": parking_spot.parking_status,
            "zone_id": parking_spot.zone.id
          }
        }
        send_data = json.dumps(tmp)
        print("TO TOKEN: "+ token)
        print(send_data)
        self.channel.basic_publish(exchange='amq.topic', routing_key=token, body=send_data)

    def run(self):
        while True:
          connection = pika.BlockingConnection(parameters)
          self.channel = connection.channel()

          print(datetime.now().strftime("%Y-%m-%d %H:%M:%s"))
          self.calculate_parking_log()
          self.channel.close()
          connection.close()          
          time.sleep(PROCESSING_INTERVAL)
          # Check every 30 seconds interval to get majority score

majority_thread = MAJORITY_Thread()
majority_thread.daemon = True
majority_thread.start()


class AMQP_Publish_Time_Thread(threading.Thread):
    channel = None
    def run(self):
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        while True:
          message = datetime.now().strftime("%c")
          try:
            print(message)
            channel.basic_publish(exchange='amq.topic', routing_key='time', body=message)
          except:
            print("Some Publish Error, skip this Time loop process")
          
          time.sleep(1)

publish_time_thread = AMQP_Publish_Time_Thread()
publish_time_thread.daemon = True
publish_time_thread.start()      

# class AMQP_Publish_Parking_Slots_thread(threading.Thread):
#     channel = None
#     def run(self):
#         while True:
#           try:
#             parking_zones = ParkingZone.objects.all()
#             for parking_zone in parking_zones:
#               # print(parking_zone)
#               publish_ParkingSpots_by_parkingzone(parking_zone)

#           except:
#             print("Some Publish Error, skip this Parking Zone loop process")

#           time.sleep(10)
        

# class AMQP_Consumer_Thread(threading.Thread):
#     channel = None
#     queue_name = ""
#     def callback_mobile_activity(self, ch, method, properties, body):
#       json_data = json.loads(body)
#       # print(json_data)

#       if json_data['action'] == 'parking_slot_registration':
#         # TODO: This is just for Admin only
#         zone = ParkingZone.objects.filter(name='All Zones').first()
#         ParkingSpot.create(
#           registrar_uuid = json_data['device_uuid'],
#           longitude = json_data['lon'],
#           latitude = json_data['lat'],
#           zone = zone
#         )

#       elif json_data['action'] == 'parking_availability':
#         # default value: available
#         self.process_participation(json_data)
#         # publish_participation_to_device_uuid(json_data['device_uuid'])

#       elif json_data['action'] == 'participant_location':
#         data_movement = ParticipantMovementLog(
#           participant_uuid = json_data['device_uuid'],
#           longitude = json_data['lon'],
#           latitude = json_data['lat']
#         )
#         data_movement.save()
        
#         Subscription.subscribe(
#           longitude=json_data['lon'], 
#           latitude=json_data['lat'], 
#           subscriber_uuid=json_data['device_uuid'],
#           subscriber_type=json_data['device_type']
#         )
#         print(data_movement)
#       # publish_participation_to_device_uuid(json_data['device_uuid'])
#       # publish_all_parkingzones_and_geopoints_to_device_uuid(json_data['device_uuid'])

#     def process_participation(self, json_data):
        
#         value_participation = 1

#         if json_data['msg'] == 'Unavailable':
#           value_participation = -1

#         new_data = ParkingAvailabilityLog(
#           participant_uuid = json_data['device_uuid'],
#           longitude = json_data['lon'],
#           latitude = json_data['lat'],
#           availability_value = value_participation
#         )
#         new_data.save()

#         participation_status, current_time = Participation.participate(
#           json_data['lon'], 
#           json_data['lat'], 
#           json_data['device_uuid'], 
#           value_participation, 
#           PROCESSING_TIME_WINDOW
#         )

#     def run(self):
#         print(' [*] Waiting for SParkeeMobile report. To exit press CTRL+C')

#         self.channel.basic_consume(on_message_callback=self.callback_mobile_activity, auto_ack=True, queue=self.queue_name)
#         self.channel.start_consuming()


# # consumer_thread = AMQP_Consumer_Thread()
# # consumer_thread.channel = channel_recv
# # consumer_thread.queue_name = queue_name_recv
# # consumer_thread.daemon = True
# # consumer_thread.start()      


# # publish_time_thread = AMQP_Publish_Time_Thread()
# # publish_time_thread.channel = channel_send
# # publish_time_thread.daemon = True
# # publish_time_thread.start()      


# # publish_parking_slots_thread = AMQP_Publish_Parking_Slots_thread()
# # publish_parking_slots_thread.channel = channel_send
# # publish_parking_slots_thread.daemon = True
# # publish_parking_slots_thread.start()      


# # credit_calculation_thread = CREDIT_Calculation_Thread()
# # credit_calculation.daemon = True
# # credit_calculation.start()

# # @background(queue="submit_background_job")
# # def submit_background_job():
# #     current_time = datetime.now()

# def publish_participation_to_device_uuid(device_uuid):
#     time_treshold = datetime.now() - timedelta(seconds=PROCESSING_TIME_WINDOW)
#     participant_credits = ParticipantCredit.objects.filter(ts_update__gt=time_treshold, participant_uuid=device_uuid).all()
#     topic = "participant." + device_uuid
#     payload_type = "participant_credits"
#     send_participant_credits_to_topic(topic, participant_credits, payload_type)


# def publish_all_parkingzones_and_geopoints_to_device_uuid(device_uuid):
#     parking_zones = ParkingZone.objects.all()
#     topic = "participant." + device_uuid
#     payload_type = "parking_zones"
#     send_parkingzones_to_topic(topic, parking_zones, payload_type)

# def publish_ParkingSpots_by_parkingzone(parking_zone):
#     parking_slots = ParkingSpot.objects.filter(zone=parking_zone).all()
#     topic = "parking_slot.zone." + str(parking_zone.id)
#     payload_type = "parking_slots"
#     send_parking_slots_to_topic(topic, parking_slots, payload_type)

# def send_participant_credits_to_topic(amqp_topic, participant_credits, payload_type):
#     list_msg = []

#     for credit in participant_credits:
#       tmp = {
#         'id_participation': credit.participation.id,
#         'id_credit': credit.id,
#         'ts_participation': credit.participation.ts_update.isoformat(),
#         'ts_credit': credit.ts_update.isoformat(),
#         'longitude': credit.participation.longitude,
#         'latitude': credit.participation.latitude,
#         'availability_value': credit.participation.availability_value,
#         'credit_value': credit.credit_value,
#         'participation_processed': credit.participation.processed,
#         'credit_processed': credit.processed
#       }
#       list_msg.append(tmp)

#     send_data = {
#       'type': payload_type,
#       'payload': list_msg
#     }

#     message = json.dumps(send_data, cls=DjangoJSONEncoder)
#     send_to_topic(amqp_topic, message, payload_type)
#     # print(message)

# def send_parkingzones_to_topic(amqp_topic, parking_zones, payload_type):

#     list_msg = []    
#     for zone in parking_zones:
#         parkingzone_geopoints = ParkingZonePolygonGeoPoint.objects.filter(parking_zone=zone).values('id', 'longitude', 'latitude')
#         list_geopoints = list(parkingzone_geopoints)
#         tmp = {
#           'id': zone.id,
#           'name': zone.name,
#           'description': zone.description,
#           'center_longitude': zone.center_longitude,
#           'center_latitude': zone.center_latitude,
#           'allowed_minimum_credit': zone.allowed_minimum_credit,
#           'geopoints': list_geopoints
#         }
#         list_msg.append(tmp)

#     send_data = {
#       'type': payload_type,
#       'payload': list_msg
#     }

#     print(send_data)
#     message = json.dumps(send_data, cls=DjangoJSONEncoder)
#     send_to_topic(amqp_topic, message, payload_type)

# def send_parking_slots_to_topic(amqp_topic, parking_slots, payload_type):
#     list_msg = []

#     for slot in parking_slots:
#       tmp = {
#         'id': slot.id,
#         'ts_register': slot.ts_register.isoformat(),
#         'ts_update': slot.ts_update.isoformat(),
#         'longitude': slot.longitude,
#         'latitude': slot.latitude,
#         'total_available': slot.total_available,
#         'total_unavailable': slot.total_unavailable,
#         'confidence_level' : slot.confidence_level,
#         'status': slot.status,
#         'zone_id': slot.zone.id,
#         'zone_name': slot.zone.name
#       }
#       list_msg.append(tmp)

#     send_data = {
#       'type': payload_type,
#       'payload': list_msg
#     }

#     # print(send_data)
#     message = json.dumps(send_data, cls=DjangoJSONEncoder)
#     send_to_topic(amqp_topic, message, payload_type)

# def send_to_topic(amqp_topic, message, payload_type):
#     try:
#       current_time = datetime.now()

#       channel_send.basic_publish(exchange='amq.topic', routing_key=amqp_topic, body=message)
#       # print(current_time.strftime("%Y-%m-%d, %H:%M:%S") + " -- Publish to Topic: " + amqp_topic + ", Payload Type: "+ payload_type )
#     except:
#       print("Some Publish Error, skip this send process")
