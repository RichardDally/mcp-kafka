import logging
import redis
from fastmcp import FastMCP
from config import settings

logging.basicConfig(level=settings.log_level, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("HistoryAPI")

mcp = FastMCP("HistoryAPI")
r = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

@mcp.tool()
def get_usage_metrics() -> str:
    """Returns a full summary of processed Kafka messages."""
    total = r.get("total_msg_count") or 0
    actions = r.hgetall("action_counts") or {}
    return f"Total: {total} | Breakdown: {actions}"

@mcp.tool()
def count_action(action_name: str) -> int:
    """Returns the count for a specific action like 'login'."""
    return int(r.hget("action_counts", action_name) or 0)

if __name__ == "__main__":
    mcp.run()
    