from flask import Flask, render_template, request, jsonify
from symptom_checker import generate_response

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    response = generate_response(user_input)
    return jsonify({"response": response})

# 🔥 THIS PART IS CRITICAL
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)