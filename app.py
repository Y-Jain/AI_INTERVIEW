from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import uuid
from groq import Groq

# --- CONFIG ---
app = Flask(__name__)
CORS(app)

# Initialize the Groq client with your API key
groq_client = Groq(api_key='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')

# Store conversation and scoring data
interview_data = {}

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_interview', methods=['POST'])
def start_interview():
    """Start the interview with an introductory question."""
    intro_question = "Hi! Let's start the interview. Can you tell me about yourself?"
    question_id = str(uuid.uuid4())  # Unique ID for the first question
    
    return jsonify({
        "question": intro_question,
        "question_id": question_id
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()

    if not data or 'messages' not in data:
        return jsonify({"error": "Invalid input"}), 400

    messages = data['messages']
    
    # Get the last message's role and content
    last_message = messages[-1]

    # If the last message is from the assistant, it means we need to ask a question
    if last_message['role'] == 'assistant':
        # Generate follow-up questions based on previous answer
        question = generate_follow_up_question(messages)

        # Create a unique question ID for tracking
        question_id = str(uuid.uuid4())

        return jsonify({
            "reply": question,
            "question_id": question_id
        })

    # If the message is from the user, score the response
    if last_message['role'] == 'user':
        user_answer = last_message['content']
        question_id = data.get('question_id')  # Ensure we get the question_id from the request

        # Score the answer using Groq
        score, explanation = score_answer_with_groq(user_answer, messages[-2]['content'])

        # Store the Q&A with the score and explanation
        if question_id:
            interview_data[question_id] = {
                "question": messages[-2]['content'],  # Get the corresponding question
                "answer": user_answer,
                "score": score,
                "explanation": explanation
            }

        return jsonify({
            "reply": "Your answer has been recorded. Thank you!",
            "score": score,
            "explanation": explanation
        })

@app.route('/save', methods=['POST'])
def save_audio():
    try:
        audio = request.files['audio']
        transcript = request.form['transcript']

        # Save the audio file and transcript
        audio.save(f"uploads/{audio.filename}")
        with open(f"uploads/{audio.filename}.txt", "w") as f:
            f.write(transcript)

        return jsonify({"message": "Audio and transcript saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_follow_up_question(messages):
    """Generate follow-up questions based on the candidate's previous answers."""
    
    # Extract candidate's last response
    last_response = messages[-1]['content']

    # Use the response to generate a follow-up question
    follow_up_prompt = f"Given the candidate's answer: {last_response}\nGenerate a relevant follow-up question."

    try:
        # Use Groq API to generate the follow-up question
        response = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",  # Replace with the Groq model you're using
            messages=[{"role": "user", "content": follow_up_prompt}],
            temperature=0.7,
            max_tokens=150,
            top_p=1,
            stream=False  # Streaming is disabled here, as it's not necessary for this case
        )

        follow_up_question = response.choices[0].delta.content.strip()
        return follow_up_question
    
    except Exception as e:
        return "Could you elaborate on your previous answer?"


def score_answer_with_groq(answer: str, question: str) -> tuple:
    try:
        prompt = f"Question: {question}\nAnswer: {answer}\n\nEvaluate the answer's accuracy and provide a score out of 5. Explain the score."
        response = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150,
            top_p=1,
            stream=False
        )
        groq_response = response.choices[0].delta.content.strip()

        if "Score:" in groq_response:
            score = int(groq_response.split("Score:")[1].split("/")[0].strip())
            explanation = groq_response.split("Score:")[1].split("\n")[1].strip()
        else:
            score = 0
            explanation = "The answer was not clear enough to assess."

        return score, explanation
    except Exception as e:
        return 0, f"Error: {str(e)}"


# --- MAIN ---

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
