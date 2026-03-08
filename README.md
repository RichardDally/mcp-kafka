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
   Spin up Kafka, Schema Registry, Kafka UI, Redis, and RedisInsight:
   ```bash
   docker-compose up -d
   ```
   * **Kafka UI:** Access via [http://localhost:8080](http://localhost:8080)
   * **RedisInsight UI:** Access via [http://localhost:8001](http://localhost:8001)
     * To connect RedisInsight to the datastore, click "Add Redis Database" and use `redis` as the Host and `6379` as the Port. Stop/Leave username and password blank.

2. **Install Dependencies**
   If you have `uv` installed:
   ```bash
   uv sync
   ```
   Otherwise, using `pip`:
   ```bash
   pip install .
   ```

3. **Prepare the Topic and Schema**
   You can easily create your topic, register the schema, and optionally feed it with dummy data:
   ```bash
   uv run mcp-kafka create-topic my-history
   uv run mcp-kafka schema
   uv run mcp-kafka feed my-history
   ```

4. **Run the Ingestor**
   Start the Kafka consumer to process messages:
   ```bash
   uv run mcp-kafka ingest
   ```

5. **Run the MCP Server**
   Start the FastMCP API to expose the data to external tools (AI agents):
   ```bash
   uv run mcp-kafka api
   ```

## Configuration
Settings are managed via Pydantic settings in `config.py`. You can override them using environment variables or a `.env` file.
