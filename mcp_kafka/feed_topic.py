import time
import random
import importlib.resources
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
from mcp_kafka.config import settings

def feed_topic(topic_name: str = "my-history"):
    # Initialize Schema Registry client
    sr_client = SchemaRegistryClient({'url': settings.schema_registry_url})
    
    # Load schema
    schema_text = importlib.resources.files("mcp_kafka").joinpath("history_schema.avsc").read_text(encoding="utf-8")
    
    # Initialize AvroSerializer
    avro_serializer = AvroSerializer(sr_client, schema_text)

    # Initialize Producer
    producer = Producer({'bootstrap.servers': settings.kafka_bootstrap_servers})

    # Action state machines to ensure enter comes before exit
    # 0 = not entered, 1 = entered
    user_states = {1: 0, 2: 0, 3: 0}
    
    def generate_action(user_id):
        state = user_states[user_id]
        if state == 0:
            user_states[user_id] = 1
            return "enter"
        else:
            # Currently entered. They can either think, play, or exit.
            action = random.choice(["think", "play", "exit"])
            if action == "exit":
                user_states[user_id] = 0
            return action

    print(f"Feeding 100 messages for each user ID to topic '{topic_name}'...")
    
    # Starting timestamp
    current_ts = int(time.time() * 1000)

    total_msgs = 0
    for _ in range(100):
        for user_id in [1, 2, 3]:
            action = generate_action(user_id)
            # Advance time by random 1-5 seconds
            current_ts += random.randint(1000, 5000) 
            
            message = {
                "user_id": user_id,
                "action": action,
                "timestamp": current_ts
            }
            
            try:
                # Serialize and produce
                producer.produce(
                    topic=topic_name,
                    value=avro_serializer(message, SerializationContext(topic_name, MessageField.VALUE))
                )
                total_msgs += 1
            except Exception as e:
                print(f"Error producing message: {e}")
                
        # Poll briefly to handle delivery callbacks
        producer.poll(0)
    
    # Wait for any outstanding messages to be delivered
    producer.flush()
    print(f"Successfully fed {total_msgs} event messages.")

if __name__ == "__main__":
    feed_topic()
