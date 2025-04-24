from flask import Flask, request, jsonify, render_template
import os, uuid, json, datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
JSON_FILE = "transcripts.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure JSON file exists
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w") as f:
        json.dump([], f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save", methods=["POST"])
def save():
    if "audio" not in request.files or "transcript" not in request.form:
        return jsonify({"message": "Missing audio or transcript"}), 400

    audio = request.files["audio"]
    transcript = request.form["transcript"]

    filename = f"{uuid.uuid4().hex}.webm"
    audio_path = os.path.join(UPLOAD_FOLDER, filename)
    audio.save(audio_path)

    record = {
        "filename": filename,
        "transcript": transcript,
        "timestamp": datetime.datetime.now().isoformat()
    }

    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    data.append(record)

    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return jsonify({"message": "Saved successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
