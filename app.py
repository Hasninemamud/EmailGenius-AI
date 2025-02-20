from flask import Flask, render_template, request, jsonify, session
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# API endpoint and headers
API_URL = "https://api.hyperbolic.xyz/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('API_KEY')}"
}

def query_llama(prompt, history=None):
    # System message to define the assistant's role and tone
    system_message = {
        "role": "system",
        "content": "You are a creative writing assistant with a vivid imagination. Your tone is encouraging and poetic, and you help users craft stories, refine ideas, or generate evocative prose."
    }
    
    # Build message history
    messages = [system_message]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    data = {
        "messages": messages,
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "max_tokens": 512,
        "temperature": 0.7,  # Slightly higher for creativity
        "top_p": 0.95
    }
    
    # Make the API request and return the response
    response = requests.post(API_URL, headers=HEADERS, json=data)
    return response.json()  # This return is correctly inside the function

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/chatAI")
def chatAI():
    session.pop("chat_history", None)  # Clear history on new chat
    return render_template("chatAI.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/generate", methods=["POST"])
def generate():
    """Handles text generation requests with formatted output"""
    prompt = request.json.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Retrieve or initialize chat history from session
    chat_history = session.get("chat_history", [])
    
    # Query the model with history
    response = query_llama(prompt, chat_history)

    # Extract and format response
    generated_text = response.get("choices", [{}])[0].get("message", {}).get("content", "No response")
    formatted_text = generated_text.replace("\n", "<br>")

    # Update chat history
    chat_history.append({"role": "user", "content": prompt})
    chat_history.append({"role": "assistant", "content": generated_text})
    session["chat_history"] = chat_history[-10:]  # Limit to last 10 messages

    return jsonify({"generated_text": formatted_text})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)