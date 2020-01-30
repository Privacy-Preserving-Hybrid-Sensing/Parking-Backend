from background_task import background
from logging import getLogger
import pika
import json
from sparkee_common.models import ParkingAvailabilityLog, ParticipantMovementLog, ParkingSlot

logger = getLogger(__name__)

# @background(schedule=1)
# def demo_task(message):
#     logger.debug('demo_task. message={0}'.format(message))
#     print("ABC123")


credentials = pika.PlainCredentials('mobile', 'ieGh4thi')
parameters = pika.ConnectionParameters(
    'ec2-3-133-91-181.us-east-2.compute.amazonaws.com',
    5672,
    '/',
    credentials
)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.exchange_declare(exchange='DEVICE_TO_SERVER', exchange_type='fanout', auto_delete=True)

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='DEVICE_TO_SERVER', queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
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

  elif json_data['type'] == 'participant_location':
    value_participation = 0
    new_data = ParticipantMovementLog(
      participant_uuid = json_data['routing_key_uuid'],
      longitude = json_data['long'],
      lattitude = json_data['latt']
    )
    new_data.save()

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()

