import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
db = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))["catalog"]

def fmt(d):
    d["id"] = str(d.pop("_id"))
    return d

@app.get("/health")
def health():
    return {"status": "UP"}

@app.post("/courses")
def create_course():
    b = request.get_json(silent=True) or {}
    if not b.get("title") or not b.get("instructorId"):
        return {"error": "title and instructorId are required"}, 400
    doc = {"title": b["title"], "instructorId": b["instructorId"],
           "category": b.get("category", "general"), "modules": b.get("modules", [])}
    r = db.courses.insert_one(doc)
    doc.pop("_id")
    doc["id"] = str(r.inserted_id)
    return doc, 201

@app.get("/courses")
def list_courses():
    cat = request.args.get("category")
    q = {"category": cat} if cat else {}
    return jsonify([fmt(c) for c in db.courses.find(q)])

@app.get("/courses/<cid>")
def get_course(cid):
    try:
        c = db.courses.find_one({"_id": ObjectId(cid)})
    except Exception:
        return {"error": "invalid id"}, 400
    if not c:
        return {"error": "course not found"}, 404
    return fmt(c)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
