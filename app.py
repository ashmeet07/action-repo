from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

client = MongoClient(os.environ.get("MONGO_STRING"))

db = client["github"]
collection = db["event"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/webhook", methods=["POST"])
def webhook():

    payload = request.json
    event_type = request.headers.get("X-GitHub-Event")

    data = {}

    if event_type == "push":

        data["request_id"] = payload["after"]
        data["author"] = payload["pusher"]["name"]
        data["action"] = "PUSH"
        data["from_branch"] = None
        data["to_branch"] = payload["ref"].split("/")[-1]
        data["timestamp"] = datetime.utcnow()

    elif event_type == "pull_request":

        pr = payload["pull_request"]

        data["request_id"] = str(pr["id"])
        data["author"] = pr["user"]["login"]
        data["action"] = "PULL_REQUEST"
        data["from_branch"] = pr["head"]["ref"]
        data["to_branch"] = pr["base"]["ref"]
        data["timestamp"] = datetime.utcnow()

        if payload["action"] == "closed" and pr["merged"]:
            data["action"] = "MERGE"

    else:
        return jsonify({"msg": "ignored"}), 200

    collection.insert_one(data)

    return jsonify({"msg": "stored"}), 200


@app.route("/event", methods=["POST"])
def store_event():

    payload = request.json

    required_fields = ["request_id", "author", "action", "to_branch"]

    for field in required_fields:
        if field not in payload:
            return jsonify({"error": f"{field} missing"}), 400

    data = {
        "request_id": payload["request_id"],
        "author": payload["author"],
        "action": payload["action"],
        "from_branch": payload.get("from_branch"),
        "to_branch": payload["to_branch"],
        "timestamp": datetime.utcnow()
    }

    collection.insert_one(data)

    return jsonify({"msg": "event stored"}), 200


@app.route("/events", methods=["GET"])
def events():

    page = int(request.args.get("page", 1))
    limit = 10
    skip = (page - 1) * limit

    results = list(
        collection.find()
        .sort("timestamp", -1)
        .skip(skip)
        .limit(limit)
    )

    for r in results:
        r["_id"] = str(r["_id"])
        r["timestamp"] = r["timestamp"].strftime("%d %b %Y • %I:%M %p UTC")

    return jsonify(results)


# ✅ CRITICAL FOR RENDER 🚀
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)