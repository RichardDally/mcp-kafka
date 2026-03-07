# kafka-history-mcp

**Kafka-to-Redis Ingestor with FastMCP API**

This project demonstrates a Model Context Protocol (MCP) server that exposes data ingested from a Kafka topic into Redis. Messages are serialized with Avro and stored in a local Schema Registry.

## Architecture

1. **Kafka Cluster:** Local Kafka broker + Schema Registry (runs via Docker Compose).
2. **Redis:** In-memory datastore for aggregating message metrics (runs via Docker Compose).
3. **Ingestor (`mcp_kafka/kafka_to_redis.py`):** Consumes messages from Kafka, deserializes Avro payloads, and aggregates counts in Redis.
4. **FastMCP API (`mcp_kafka/mcp_api.py`):** Provides MCP tools (`get_usage_metrics`, `count_action`) for AI agents to query the aggregated data.

## Prerequisites
- Docker and Docker Compose
- Python 3.14+
- `uv` (recommended for dependency management)

## Setup

1. **Start Infrastructure**
   Spin up Kafka, Schema Registry, Kafka UI, and Redis:
   ```bash
   docker-compose up -d
   ```
   *Kafka UI is available at http://localhost:8080*

2. **Install Dependencies**
   If you have `uv` installed:
   ```bash
   uv sync
   ```
   Otherwise, using `pip`:
   ```bash
   pip install .
   ```

3. **Run the Ingestor**
   Start the Kafka consumer to process messages:
   ```bash
   python -m mcp_kafka.kafka_to_redis
   ```

4. **Run the MCP Server**
   Start the FastMCP API to expose the data to external tools:
   ```bash
   python -m mcp_kafka.mcp_api
   ```

## Configuration
Settings are managed via Pydantic settings in `config.py`. You can override them using environment variables or a `.env` file.
