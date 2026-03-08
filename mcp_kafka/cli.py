import typer
import signal
from typing import Optional

app = typer.Typer(help="CLI to manage Kafka MCP services (ingest, api, schema).")

@app.command()
def start_ingestor():
    """Start the Kafka to Redis ingestor."""
    from mcp_kafka.kafka_to_redis import Ingestor
    ingestor_srv = Ingestor()
    
    # Catch termination signals to stop cleanly
    signal.signal(signal.SIGINT, ingestor_srv.stop)
    signal.signal(signal.SIGTERM, ingestor_srv.stop)
    
    ingestor_srv.start()

@app.command()
def start_api():
    """Start the FastMCP API."""
    from mcp_kafka.mcp_server import mcp
    mcp.run()

@app.command()
def upload_schema():
    """Upload the Avro schema to the Schema Registry."""
    from mcp_kafka.upload_schema import register_schema
    register_schema()

@app.command()
def create_topic(topic_name: str = "my-history", schema_id: Optional[int] = typer.Option(None, help="Optional Schema ID to enable validation")):
    """Create a new Kafka topic. Optionally pass a Schema ID to enable Confluent value schema validation."""
    from mcp_kafka.create_topic import create_kafka_topic
    create_kafka_topic(topic_name, schema_id=schema_id)

@app.command()
def feed(topic_name: str = "my-history"):
    """Feed the specified Kafka topic with 300 sequential dummy records across 3 user IDs."""
    from mcp_kafka.feed_topic import feed_topic
    feed_topic(topic_name=topic_name)

if __name__ == "__main__":
    app()
