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
        
        import importlib.resources
        import pathlib
        
        try:
            # When running from a built wheel / installed package
            schema_text = importlib.resources.files("mcp_kafka").joinpath("history_schema.avsc").read_text()
        except Exception:
            # Fallback for local script execution
            schema_path = pathlib.Path(__file__).parent / "history_schema.avsc"
            schema_text = schema_path.read_text(encoding="utf-8")

        self.avro_deser = AvroDeserializer(sr_client, schema_text)

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
            import json
            while self.running:
                msg = self.consumer.poll(1.0)
                if msg is None: continue
                
                val = None
                try:
                    # Attempt Confluent Schema Registry Avro deserialization
                    val = self.avro_deser(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
                except Exception as e:
                    # Fallback if there is no magic byte (e.g., standard JSON sent manually from Kafka UI)
                    try:
                        val = json.loads(msg.value().decode('utf-8'))
                    except Exception as json_e:
                        logger.warning(f"Failed to deserialize message: AvroError({e}), JSONError({json_e}). Skipping.")
                        continue
                
                if val:
                    action = val.get('action')
                    if action:
                        pipe = self.r.pipeline()
                        pipe.incr("total_msg_count")
                        pipe.hincrby("action_counts", action, 1)
                        pipe.execute()
                        logger.info(f"Pushed data to Redis: action '{action}'")
        finally:
            self.consumer.close()
            logger.info("Clean shutdown complete.")

if __name__ == "__main__":
    ingestor = Ingestor()
    signal.signal(signal.SIGINT, ingestor.stop)
    ingestor.start()