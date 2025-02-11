import os
from datetime import datetime
from dotenv import load_dotenv
import redis
import numpy as np
from sentence_transformers import SentenceTransformer
from twilio.rest import Client
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Skip dotenv in production


# Redis configuration
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")

# Twilio configuration
twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
twilio_to_number = os.getenv("TWILIO_TO_NUMBER")

# Initialize Redis client
redis_client = redis.Redis(
    host=redis_host,
    port=int(redis_port),
    username="default",
    password=redis_password,
    ssl=False,
    decode_responses=False
)

# Initialize the embedding model
embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_todays_events() -> str:
    """Retrieve events happening today from Redis vector store"""
    try:
        # Get today's date in the format stored in Redis
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Create a query focused on today's date
        query = f"Events happening on {today}"
        
        # Encode the query text
        query_embedding = embed_model.encode(query)
        query_embedding_bytes = query_embedding.astype(np.float32).tobytes()

        # Perform vector search
        results = redis_client.execute_command(
            'FT.SEARCH', 'idx:events',
            "*=>[KNN 5 @embedding $BLOB AS vector_score]",
            'PARAMS', '2', 'BLOB', query_embedding_bytes,
            'DIALECT', '2',
            'SORTBY', 'vector_score',
            'RETURN', '4', 'name', 'description', 'date', 'vector_score',
            'LIMIT', '0', '5'
        )

        # Format the results
        todays_events = []
        if results and len(results) > 1:
            for i in range(1, len(results), 2):
                event_data = results[i + 1]
                event_info = {
                    event_data[i].decode('utf-8'): event_data[i + 1].decode('utf-8')
                    for i in range(0, len(event_data), 2)
                }
                
                # Only include events that are happening today
                if event_info.get('date') == today:
                    todays_events.append(
                        f"Event: {event_info.get('name', 'N/A')}\n"
                        f"Description: {event_info.get('description', 'N/A')}"
                    )

        if todays_events:
            return "\n\n".join(todays_events)
        else:
            return "No events scheduled for today."
            
    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        return f"Error retrieving events: {str(e)}"

def send_sms_notification(message: str):
    """Send SMS notification using Twilio"""
    try:
        # Initialize Twilio client
        client = Client(twilio_account_sid, twilio_auth_token)
        
        # Send message
        message = client.messages.create(
            body=message,
            from_=twilio_from_number,
            to=twilio_to_number
        )
        
        logger.info(f"SMS sent successfully! SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        return False

def main():
    """Main function to get events and send notifications"""
    try:
        # Test Redis connection
        redis_client.ping()
        logger.info("Successfully connected to Redis")
        
        # Get today's events
        events_message = get_todays_events()
        
        # Send SMS notification
        if send_sms_notification(events_message):
            logger.info("Daily events notification sent successfully")
        else:
            logger.error("Failed to send daily events notification")
            
    except redis.RedisError as e:
        logger.error(f"Redis connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main() 