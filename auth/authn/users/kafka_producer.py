from kafka import KafkaProducer
import json

PRODUCER_AUTH_SERVICE = "auth_service"


# produce json messages
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda m: json.dumps(m).encode('utf-8'), retries=3,
    api_version=(2, 0)
)
