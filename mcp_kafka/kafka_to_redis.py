import logging
import signal
import redis
from config import settings
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

logging.basicConfig(level=settings.log_level, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("Ingestor")

class Ingestor:
    def __init__(self):
        self.running = True
        self.r = redis.Redis(
            host=settings.redis_host, 
            port=settings.redis_port, 
            db=settings.redis_db, 
            decode_responses=True
        )
        
        sr_client = SchemaRegistryClient({'url': settings.schema_registry_url})
        with open("history_schema.avsc") as f:
            self.avro_deser = AvroDeserializer(sr_client, f.read())

        self.consumer = Consumer({
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'group.id': settings.kafka_group_id,
            'auto.offset.reset': 'earliest'
        })

    def stop(self, sig, frame):
        logger.info("Shutdown signal received.")
        self.running = False

    def start(self):
        self.consumer.subscribe([settings.kafka_topic])
        logger.info("Ingestor started. Monitoring Kafka...")
        try:
            while self.running:
                msg = self.consumer.poll(1.0)
                if msg is None: continue
                
                val = self.avro_deser(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
                action = val.get('action')
                
                pipe = self.r.pipeline()
                pipe.incr("total_msg_count")
                pipe.hincrby("action_counts", action, 1)
                pipe.execute()
        finally:
            self.consumer.close()
            logger.info("Clean shutdown complete.")

if __name__ == "__main__":
    ingestor = Ingestor()
    signal.signal(signal.SIGINT, ingestor.stop)
    ingestor.start()