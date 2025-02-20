from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# API endpoint and headers
API_URL = "https://api.hyperbolic.xyz/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXNuaW5laGVtZWw4NUBnbWFpbC5jb20iLCJpYXQiOjE3Mzk1NjM2ODB9.EvhP5MqdQCxyr86WSisIIzAekMdTBZ788J7qd87kg28"
}

import requests

def query_llama(prompt):
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "max_tokens": 512,
        "temperature": 0.1,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=data)
        response_json = response.json()

        # Log the full response
        print("API Response:", response_json)

        if "choices" in response_json and response_json["choices"]:
            return response_json
        else:
            return {"error": "Invalid response format from API"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/chatAI")
def chatAI():
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

    response = query_llama(prompt)

    # Check if API returned an error
    if "error" in response:
        return jsonify({"error": response["error"]}), 500

    # Extract response text safely
    generated_text = response.get("choices", [{}])[0].get("message", {}).get("content", "No response")

    # Format response for HTML rendering
    formatted_text = generated_text.replace("\n", "<br>")

    return jsonify({"generated_text": formatted_text})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
