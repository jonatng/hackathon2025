import os
import redis
import logging
import numpy as np
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Redis configuration from environment variables (or defaults for testing)
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")
redis_username = os.getenv("REDIS_USERNAME")

# Initialize Redis client.
# Note: decode_responses is False because the vector field is binary.
redis_client = redis.Redis(
    host=redis_host,
    port=int(redis_port),
    username=redis_username,
    password=redis_password,
    ssl=False,
    decode_responses=False
)

# Initialize the embedding model
embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def simple_search():
    """Perform a simple search (without vector clause) to read all events."""
    try:
        # This returns all documents in the index.
        results = redis_client.execute_command("FT.SEARCH", "idx:events", "*")
        logger.info("Simple FT.SEARCH '*' results:\n%s", results)
    except Exception as e:
        logger.error("Error during simple search: %s", e)

def vector_search_test(query_text):
    """Perform a vector search for debugging.

    This function encodes the query text, converts it to raw bytes, and
    executes a vector search query that explicitly aliases the vector similarity
    score as `vector_score`. The query then sorts and returns results using that alias.
    """
    try:
        # Encode the test query using the embedding model.
        query_embedding = embed_model.encode(query_text)
        query_embedding_bytes = query_embedding.astype(np.float32).tobytes()

        # Build and execute the vector search query.
        # The query uses a combined query string with the vector clause and
        # explicitly aliases the computed similarity score as "vector_score".
        results = redis_client.execute_command(
            'FT.SEARCH', 'idx:events',
            "*=>[KNN 3 @embedding $BLOB AS vector_score]",
            'PARAMS', '2', 'BLOB', query_embedding_bytes,
            'DIALECT', '2',
            'SORTBY', 'vector_score',
            'RETURN', '2', 'name', 'vector_score',
            'LIMIT', '0', '3'
        )
        logger.info("Vector search results for query '%s':\n%s", query_text, results)
    except Exception as e:
        logger.error("Vector search error: %s", e)

if __name__ == "__main__":
    logger.info("Starting simple search...")
    simple_search()

    test_query = "art workshop"
    logger.info("Starting vector search for query: '%s'...", test_query)
    vector_search_test(test_query)
