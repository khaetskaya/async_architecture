from kafka import KafkaProducer
import json

PRODUCER_TASK_TRACKER_SERVICE = "task_tracker_service"

# produce json messages
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda m: json.dumps(m).encode('utf-8'), retries=3,
    api_version=(2, 0),
    batch_size=5,
)
