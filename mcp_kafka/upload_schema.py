import os
from pathlib import Path
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from mcp_kafka.config import settings

def register_schema():
    # 1. Initialize the Schema Registry Client
    sr_client = SchemaRegistryClient({'url': settings.schema_registry_url})
    
    # 2. Load the schema from the file
    schema_path = Path(__file__).parent / "history_schema.avsc"
    schema_text = schema_path.read_text(encoding="utf-8")
    
    # 3. Create a Schema object
    avro_schema = Schema(schema_text, schema_type="AVRO")
    
    # 4. Define the subject name (usually topic-name-value)
    subject = f"{settings.kafka_topic}-value"
    
    # 5. Register the schema
    try:
        schema_id = sr_client.register_schema(subject_name=subject, schema=avro_schema)
        print(f"Successfully registered schema for subject '{subject}'.")
        print(f"Schema ID: {schema_id}")
    except Exception as e:
        print(f"Failed to register schema: {e}")

if __name__ == "__main__":
    register_schema()
