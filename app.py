from flask import Flask, request, jsonify,render_template
from interview_brain import InterviewBrain
import json
import os

app = Flask(__name__)

# Initialize InterviewBrain
api_key = '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'
model_config = {
    "model": "llama-3.1-8b-instant",
    "temperature": 0.5,
    "max_tokens": 150,
    "top_p": 1,
    "stream": False
}
interview_brain = InterviewBrain(api_key, model_config)

# Store interview data
interview_data = {
    "questions": [],
    "responses": [],
    "scores": []
}



@app.route('/')
def index():
    return render_template('index.html')
# Endpoint to start the interview and fetch the first question
@app.route('/start_interview', methods=['GET'])
def start_interview():
    try:
        # Generate the first question dynamically
        question = interview_brain.generate_question()
        return jsonify({"question": question}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to process voice input and generate a response
@app.route('/process_voice', methods=['POST'])
def process_voice():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Invalid input"}), 400

        user_text = data['text']
        follow_up_questions = data.get('follow_up_questions', {})

        # Generate the next question dynamically based on the user's response
        question = interview_brain.generate_question(follow_up_questions)

        # Generate a score and explanation for the user's response
        score, explanation = interview_brain.generate_score(question, user_text)

        # Save the question, response, and score
        interview_data["questions"].append(question)
        interview_data["responses"].append(user_text)
        interview_data["scores"].append({
            "score": score,
            "explanation": explanation
        })

        return jsonify({
            "question": question,
            "score": score,
            "explanation": explanation
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to save the complete conversation as a JSON file
@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    try:
        file_path = os.path.join(os.getcwd(), "conversation.json")
        with open(file_path, 'w') as f:
            json.dump(interview_data, f, indent=4)
        return jsonify({"message": "Conversation saved successfully", "file_path": file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to end the interview
@app.route('/end_interview', methods=['POST'])
def end_interview():
    try:
        # Save the conversation before ending
        save_conversation()
        return jsonify({"message": "Interview ended successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save', methods=['POST'])
def save_audio_and_transcript():
    try:
        # Save the audio file
        audio = request.files.get('audio')
        transcript = request.form.get('transcript')

        if not audio or not transcript:
            return jsonify({"error": "Audio or transcript missing"}), 400

        # Save audio to a file
        audio_path = os.path.join(os.getcwd(), "saved_audio.webm")
        with open(audio_path, 'wb') as f:
            f.write(audio.read())

        # Save transcript to a file
        transcript_path = os.path.join(os.getcwd(), "transcript.txt")
        with open(transcript_path, 'w') as f:
            f.write(transcript)

        return jsonify({"message": "Audio and transcript saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)