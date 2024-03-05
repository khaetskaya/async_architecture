from kafka import KafkaConsumer
import json


# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer(
    bootstrap_servers=['localhost:9092'],
    group_id='async_arc',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    api_version=(2, 0)
)
