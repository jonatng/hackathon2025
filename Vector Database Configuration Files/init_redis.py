import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import redis
import os
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Excel file path
EXCEL_PATH = Path(os.getenv('EXCEL_PATH', os.path.dirname(__file__)))  # Default to the current directory if not set
EXCEL_FILE = Path(os.getenv('EXCEL_FILE', 'events.xlsx'))  # Default filename if not set
EXCEL_FILE = EXCEL_PATH / EXCEL_FILE

# Validate Excel path configuration
if not EXCEL_PATH.exists():
    raise ValueError(f"Excel directory path does not exist: {EXCEL_PATH}")

# Redis configuration
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")
redis_username = os.getenv("REDIS_USERNAME", "default")  # Make username configurable

if not all([redis_host, redis_port, redis_password]):
    raise ValueError("Redis configuration incomplete. Check environment variables.")

# Initialize Redis client with decode_responses=False so we can store binary data
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

def create_vector_index():
    """Create Redis vector similarity index if it doesn't exist"""
    try:
        # Try to get index info. If the index exists, this command will succeed.
        redis_client.execute_command("FT.INFO", "idx:events")
        logger.info("Vector index already exists")
    except Exception:
        logger.info("Vector index does not exist. Creating index...")
        # Create index with vector configuration.
        # The vector field is defined as a FLAT index with:
        # - 6: Additional parameter (block size / number of arguments required)
        # - TYPE FLOAT32: Data type of the vector
        # - DIM 384: Dimension of the vector (matches the model output)
        # - DISTANCE_METRIC COSINE: Similarity metric to use.
        schema = [
            'FT.CREATE', 'idx:events',
            'ON', 'HASH',
            'PREFIX', '1', 'event:',
            'SCHEMA',
            'name', 'TEXT',
            'description', 'TEXT',
            'date', 'TEXT', 'SORTABLE',
            'start_time', 'TEXT', 'SORTABLE',
            'end_time', 'TEXT', 'SORTABLE',
            'location', 'TEXT',
            'organizer', 'TEXT',
            'resident_participants', 'TEXT',
            'embedding', 'VECTOR', 'FLAT', '6', 'TYPE', 'FLOAT32', 'DIM', '384', 'DISTANCE_METRIC', 'COSINE'
        ]
        
        try:
            redis_client.execute_command(*schema)
            logger.info("Created vector similarity index")
        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
            raise

def test_vector_search(test_embedding):
    """Test vector similarity search functionality"""
    try:
        # Convert the test embedding to raw bytes (no base64 encoding)
        test_vector_bytes = test_embedding.astype(np.float32).tobytes()

        # Adjusted query string: note the space between '*' and '=>[...]'
        results = redis_client.execute_command(
            'FT.SEARCH', 'idx:events', '* =>[KNN 3 @embedding $BLOB]',
            'PARAMS', '2', 'BLOB', test_vector_bytes,
            'SORTBY', '__vector_score',
            'RETURN', '2', 'name', '__vector_score',
            'LIMIT', '0', '3'
        )
        
        logger.info(f"Vector similarity search results: {results}")
        return True
    except Exception as e:
        logger.error(f"Vector search test failed: {e}")
        return False

def clean_date(date_str):
    """Convert Excel date to string format"""
    try:
        if pd.isna(date_str):
            return None
        if isinstance(date_str, datetime):
            return date_str.strftime('%Y-%m-%d')
        return str(date_str)
    except Exception as e:
        logger.warning(f"Date conversion error: {e}")
        return None

def clean_time(time_str):
    """Clean and format time strings"""
    try:
        if pd.isna(time_str):
            return None
        if isinstance(time_str, datetime):
            # Correctly reference the time variable here.
            return time_str.strftime('%H:%M:%S')
        if isinstance(time_str, str):
            # If it's a string containing a full timestamp, convert to datetime first.
            try:
                dt = pd.to_datetime(time_str)
                return dt.strftime('%H:%M:%S')
            except Exception:
                return time_str
        return str(time_str)
    except Exception as e:
        logger.warning(f"Time conversion error: {e}")
        return None

def initialize_events_database():
    """Load events into Redis with vector embeddings"""
    try:
        # Check if Excel file exists
        if not EXCEL_FILE.exists():
            raise FileNotFoundError(f"Excel file not found at {EXCEL_FILE}")

        # Load events from Excel
        events_df = pd.read_excel(EXCEL_FILE)
        logger.info(f"Loaded {len(events_df)} events from Excel file")

        # Create vector index (if needed)
        create_vector_index()

        # Process each event
        for _, event in events_df.iterrows():
            # Clean date and time fields
            event_date = clean_date(event['EVENT_DATE'])
            start_time = clean_time(event['START_TIME'])
            end_time = clean_time(event['END_TIME'])
            
            if not event_date or not start_time:
                logger.warning(f"Skipping event '{event['EVENT_NAME']}' due to invalid date/time")
                continue

            # Create combined text for embedding (excluding timestamps)
            event_text = (
                f"{event['EVENT_NAME']} - {event['EVENT_DESCRIPTION']} on {event_date} "
                f"at {event['LOCATION']} from {start_time} to {end_time}"
            )
            
            # Generate embedding using the SentenceTransformer model
            embedding = embed_model.encode(event_text)
            
            # Convert embedding to raw bytes for Redis storage
            embedding_bytes = embedding.astype(np.float32).tobytes()
            
            # Use EVENT_ID if available, otherwise generate an id based on the event name
            event_id = str(event.get('EVENT_ID', event['EVENT_NAME'].lower().replace(' ', '_')))
            event_key = f"event:{event_id}"
            
            # Prepare event data to store in Redis.
            # Note: All non-vector fields are stored as strings.
            event_data = {
                'id': event_id,
                'name': str(event['EVENT_NAME']),
                'description': str(event['EVENT_DESCRIPTION']),
                'date': event_date,
                'start_time': start_time,
                'end_time': end_time,
                'location': str(event['LOCATION']),
                'organizer': str(event['ORGANIZER']),
                'resident_participants': str(event.get('RESIDENT_PARTICIPATION', '')),
                'embedding': embedding_bytes
            }
            
            # Optionally add created_at and updated_at if available
            if 'CREATED_AT' in event:
                event_data['created_at'] = clean_date(event['CREATED_AT'])
            if 'UPDATED_AT' in event:
                event_data['updated_at'] = clean_date(event['UPDATED_AT'])
            
            # Store the event in Redis as a hash
            redis_client.hset(event_key, mapping=event_data)
            logger.info(f"Stored event: {event['EVENT_NAME']}")

        logger.info("Successfully initialized events database")
        
        # Test vector similarity search
        test_query = "art workshop"
        test_embedding = embed_model.encode(test_query)
        if test_vector_search(test_embedding):
            logger.info("Vector similarity search is working correctly")
        else:
            logger.warning("Vector similarity search test failed")
        
    except Exception as e:
        logger.error(f"Error initializing events database: {e}")
        raise

if __name__ == "__main__":
    initialize_events_database()

