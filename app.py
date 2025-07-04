from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB setup (local)
client = MongoClient("mongodb://localhost:27017/")
db = client["github_webhooks"]
events = db["events"]

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    payload = None

    if event_type == "push":
        payload = {
            "request_id": data.get("after"),
            "author": data.get("pusher", {}).get("name", "unknown"),
            "action": "PUSH",
            "from_branch": data.get("ref", "").split("/")[-1],
            "to_branch": data.get("ref", "").split("/")[-1],
            "timestamp": datetime.utcnow().isoformat()
        }
    elif event_type == "pull_request":
        action = data.get("action", "").upper()
        if action == "OPENED":
            payload = {
                "request_id": str(data["pull_request"]["id"]),
                "author": data["pull_request"]["user"]["login"],
                "action": "PULL_REQUEST",
                "from_branch": data["pull_request"]["head"]["ref"],
                "to_branch": data["pull_request"]["base"]["ref"],
                "timestamp": datetime.utcnow().isoformat()
            }
        elif action == "CLOSED" and data["pull_request"].get("merged"):
            payload = {
                "request_id": str(data["pull_request"]["id"]),
                "author": data["pull_request"]["user"]["login"],
                "action": "MERGE",
                "from_branch": data["pull_request"]["head"]["ref"],
                "to_branch": data["pull_request"]["base"]["ref"],
                "timestamp": datetime.utcnow().isoformat()
            }
    if payload:
        events.insert_one(payload)
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "ignored"}), 200

@app.route('/events')
def get_events():
    result = []
    for event in events.find().sort("timestamp", -1):
        event["_id"] = str(event["_id"])
        result.append(event)
    return jsonify(result)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
