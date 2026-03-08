from confluent_kafka.admin import AdminClient, NewTopic
from mcp_kafka.config import settings
from typing import Optional

def create_kafka_topic(topic_name: str, partitions: int = 1, replication_factor: int = 1, schema_id: Optional[int] = None):
    admin_client = AdminClient({'bootstrap.servers': settings.kafka_bootstrap_servers})
    
    config = {}
    if schema_id is not None:
        # Enable schema validation (Supported in Confluent Server / cp-kafka image!)
        config['confluent.value.schema.validation'] = 'true'
        
    new_topic = NewTopic(
        topic_name, 
        num_partitions=partitions, 
        replication_factor=replication_factor,
        config=config
    )
    
    # create_topics returns a dict mapping topic name to a future
    fs = admin_client.create_topics([new_topic])
    for topic, f in fs.items():
        try:
            f.result()  # The result will be None if successful
            print(f"Successfully created topic: '{topic}'")
            if schema_id is not None:
                print(f"Enabled schema validation for topic '{topic}'. Validating against Schema ID: {schema_id}")
        except Exception as e:
            print(f"Failed to create topic '{topic}': {e}")
