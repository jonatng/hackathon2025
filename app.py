from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient
import os
import json
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
    prompt = data.get("prompt", "hello how is your day going?")
    # Call the language model
    try:
        generated_text = call_llm(llm_client, prompt)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    # Return the model's response
    return jsonify({"status": "success", "generated_text": generated_text})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 