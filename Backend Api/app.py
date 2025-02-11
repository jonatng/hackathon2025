from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient
import os
import json
from uuid import uuid4
import random
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

# Load .env file if it exists (local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Skip dotenv in production

app = Flask(__name__)
CORS(app)

# Read environment variables
hf_token = os.getenv("HF_TOKEN")
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")

if not hf_token:
    raise ValueError("Hugging Face token not found. Please set the HF_TOKEN environment variable.")
if not all([redis_host, redis_port, redis_password]):
    raise ValueError("Redis configuration incomplete. Please set REDIS_HOST, REDIS_PORT, and REDIS_PASSWORD.")

# Initialize Redis client
redis_client = redis.Redis(
    host=redis_host,
    port=int(redis_port),
    username="default",
    password=redis_password,
    ssl=False,  # Try without SSL
    decode_responses=False  # Set to False because vector field is binary
)

# Initialize the embedding model for vector search
embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

try:
    # Test connection on startup
    redis_client.ping()
    logger.info("Successfully connected to Redis")
except redis.RedisError as e:
    logger.error(f"Redis connection failed: {str(e)}")
    logger.error(f"Redis connection details: host={redis_host}, port={redis_port}")
    raise

# Initialize the InferenceClient
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
llm_client = InferenceClient(
    model=repo_id,
    token=hf_token,
    timeout=120,
)


game_sessions = {}  # Keep this for now, could be moved to Redis later too

def call_medical_assistant(inference_client: InferenceClient, prompt: str):
    """Function specifically for medical assistant responses"""
    try:
        # Vector search
        relevant_context = get_relevant_medical_context(prompt)
        
        formatted_prompt = (
    "You are an AI medical expert whose primary role is to provide accurate and concise medical advice. "
    "Your main focus should be on addressing health-related questions and concerns. "
    "You have access to the following events information, but only reference it if the user explicitly asks about events. "
    "If the user's query is medical in nature, do not include details about events.\n\n"
    "Events information (use only if relevant):\n"
    f"{relevant_context}\n\n"
    "Based on the context above, please provide a clear and concise response to the following query. "
    "If the query explicitly pertains to events, list the relevant events along with their dates; otherwise, focus on the medical advice.\n\n"
    f"User: {prompt}\n"
    "Assistant:"
)
        
        response = inference_client.text_generation(
            formatted_prompt,
            max_new_tokens=500,
            temperature=0.7,
            do_sample=True,
        )
        
        # The response is already cleaned up by the text_generation method
        cleaned_response = response
        
        return cleaned_response
    except redis.RedisError as e:
        logger.error(f"Redis error during event context retrieval: {e}")
        raise RuntimeError("Unable to access events database")
    except Exception as e:
        logger.error(f"Unexpected error in assistant: {e}")
        raise

def get_relevant_medical_context(prompt: str) -> str:
    """Retrieve relevant medical context from Redis vector store"""
    try:
        # Encode the query text using the embedding model
        query_embedding = embed_model.encode(prompt)
        query_embedding_bytes = query_embedding.astype(np.float32).tobytes()

        # Perform vector search to find most relevant events
        results = redis_client.execute_command(
            'FT.SEARCH', 'idx:events',
            "*=>[KNN 3 @embedding $BLOB AS vector_score]",
            'PARAMS', '2', 'BLOB', query_embedding_bytes,
            'DIALECT', '2',
            'SORTBY', 'vector_score',
            'RETURN', '4', 'name', 'description', 'date', 'vector_score',
            'LIMIT', '0', '3'
        )

        # Format the results into a readable context string
        context_parts = []
        if results and len(results) > 1:  # Results[0] is the total count
            for i in range(1, len(results), 2):  # Skip through the results array
                event_data = results[i + 1]  # Get the dictionary of event data
                # Convert from Redis hash format to readable text
                event_info = {
                    event_data[i].decode('utf-8'): event_data[i + 1].decode('utf-8')
                    for i in range(0, len(event_data), 2)
                }
                context_parts.append(
                    f"Event: {event_info.get('name', 'N/A')}\n"
                    f"Date: {event_info.get('date', 'N/A')}\n"
                    f"Description: {event_info.get('description', 'N/A')}"
                )

        context = "\n\n".join(context_parts)
        return context if context else "No relevant events found."
        
    except Exception as e:
        logger.error(f"Error retrieving medical context: {e}")
        return "Error retrieving event information."

def call_game_assistant(inference_client: InferenceClient, prompt: str, year: int):
    """Function specifically for historical game responses"""
    formatted_prompt = (
        f"You are an AI assistant living in the year {year}. This is a guessing game where users must figure out "
        "what year you are from based on your knowledge and responses. "
        "EXTREMELY IMPORTANT RULES:\n"
        "1. NEVER reveal the year you are from - this is the most important rule\n"
        "2. NEVER confirm or deny specific years or decades\n"
        "3. Only talk about events, culture, and technology that existed in your time\n"
        "4. If asked about the year or time period, deflect the question politely\n"
        "5. Keep responses focused and concise - maximum two sentences\n\n"
        f"User: {prompt}\n"
        "Assistant:"
    )
    
    response = inference_client.text_generation(
        formatted_prompt,
        max_new_tokens=200,
        temperature=0.7,
        do_sample=True,
    )
    
    # Clean up any remaining whitespace and get only first two sentences
    cleaned_response = response.strip()
    sentences = [s.strip() for s in cleaned_response.split('.') if s.strip()]
    cleaned_response = '. '.join(sentences[:2]) + '.'
    
    return cleaned_response

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "success", "message": "Hugging Space server is running normally"})

@app.route('/api/data', methods=['POST'])
def get_data():
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"status": "error", "message": "No prompt provided in request"}), 400
    
    user_prompt = data['prompt']
    
    # Get or create a session_id
    session_id = data.get("session_id")
    if not session_id:
        session_id = str(uuid4())

    # Retrieve conversation history from Redis
    history_key = f"conversation:{session_id}"
    try:
        history = redis_client.lrange(history_key, 0, -1)  # Get all messages
        logger.info(f"Retrieved conversation history for session {session_id}")
    except redis.RedisError as e:
        logger.error(f"Failed to retrieve conversation history: {e}")
        history = []  # Fallback to empty history

    # Call the medical assistant
    try:
        generated_text = call_medical_assistant(llm_client, user_prompt)
    except Exception as e:
        logger.error(f"Medical assistant error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

    # Append conversation history in Redis
    try:
        redis_client.rpush(history_key, f"User: {user_prompt}")
        redis_client.rpush(history_key, f"Bot: {generated_text}")
        logger.info(f"Successfully stored conversation in Redis for session {session_id}")
        redis_client.expire(history_key, 24 * 60 * 60)  # 24 hours in seconds
    except redis.RedisError as e:
        logger.error(f"Failed to store conversation in Redis: {e}")
        # Continue execution since we still have the response

    return jsonify({
        "status": "success",
        "generated_text": generated_text,
        "session_id": session_id
    })

@app.route('/api/game/start', methods=['POST'])
def start_game():
    data = request.get_json()
    visitor_id = data.get('visitorId')
    
    if not visitor_id:
        return jsonify({"status": "error", "message": "No visitor ID provided"}), 400
    
    # Initialize or reset game session
    hidden_year = random.randint(1950, 1980)
    game_sessions[visitor_id] = {
        "hidden_year": hidden_year,
        "questions_asked": [],
        "guesses": []
    }
    
    return jsonify({
        "status": "success",
        "message": "New game started",
        "debug_year": hidden_year  # Remove in production
    })

@app.route('/api/game/question', methods=['POST'])
def ask_question():
    data = request.get_json()
    visitor_id = data.get('visitorId')
    question = data.get('question')
    
    if not visitor_id or not question:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    session = game_sessions.get(visitor_id)
    if not session:
        return jsonify({"status": "error", "message": "No active game session"}), 404
    
    # Add question to history
    session['questions_asked'].append(question)
    
    try:
        # Use the game-specific LLM function
        response = call_game_assistant(llm_client, question, session['hidden_year'])
        return jsonify({"status": "success", "answer": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/game/guess', methods=['POST'])
def make_guess():
    data = request.get_json()
    visitor_id = data.get('visitorId')
    guess = data.get('guess')
    
    if not visitor_id or guess is None:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    session = game_sessions.get(visitor_id)
    if not session:
        return jsonify({"status": "error", "message": "No active game session"}), 404
    
    # Record the guess
    session['guesses'].append(guess)
    
    # Check if correct
    correct = guess == session['hidden_year']
    message = f"{'Correct' if correct else 'Incorrect'}! The year was {session['hidden_year']}"
    
    return jsonify({
        "status": "success",
        "correct": correct,
        "message": message,
        "questions_asked": len(session['questions_asked']),
        "total_guesses": len(session['guesses'])
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860) 








    