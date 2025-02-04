from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient
import os
import json
from uuid import uuid4

app = Flask(__name__)
CORS(app)

# Read the Hugging Face token from an environment variable
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("Hugging Face token not found. Please set the HF_TOKEN environment variable.")

# Initialize the InferenceClient with the model repository ID
repo_id = "microsoft/Phi-3-mini-4k-instruct"
llm_client = InferenceClient(
    model=repo_id,
    token=hf_token,
    timeout=120,
)

# A simple in-memory store for conversation history
conversations = {}

def call_llm(inference_client: InferenceClient, prompt: str):
    response = inference_client.post(
        json={
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200},
            "task": "text-generation",
        },
    )
    return json.loads(response.decode())[0]["generated_text"]

@app.route('/api/data', methods=['POST'])
def get_data():
    # Parse JSON request
    data = request.get_json()
    
    # Check if prompt is provided in the request
    if not data or 'prompt' not in data:
        return jsonify({"status": "error", "message": "No prompt provided in request"}), 400
    
    user_prompt = data['prompt']
    
    # Get or create a session_id
    session_id = data.get("session_id")
    if not session_id:
        session_id = str(uuid4())  # generate a unique session id for new sessions
        conversations[session_id] = []  # initialize conversation history

    # Retrieve conversation history; if not found, initialize it
    history = conversations.get(session_id, [])
    
    # Append the new user prompt to the history
    history.append(f"User: {user_prompt}")
    
    # Create a composite prompt by joining the history
    composite_prompt = "\n".join(history)
    
    # Call the language model with the composite prompt
    try:
        generated_text = call_llm(llm_client, composite_prompt)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    # Append the response to the history
    history.append(f"Bot: {generated_text}")
    conversations[session_id] = history  # save it back

    # Return the model's response along with the session id
    return jsonify({"status": "success", "generated_text": generated_text, "session_id": session_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 