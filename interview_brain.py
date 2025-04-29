from groq import Groq
groq_client = Groq(api_key='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')

follow_up_questions = {}

def get_resume_parsed_data():
    """Parse the resume text and extract relevant information."""
    # Placeholder function to parse resume text
    # This should return a dictionary with parsed data
    return {
        "name": "John Doe",
        "skills": ["Python", "Machine Learning"],
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Software Engineer",
                "duration": "2 years"
            }
        ]
    }

def generate_question(follow_up={}):
    prompt = f"Generate the question based on the resume data: {get_resume_parsed_data()} and the previous question and response of the candidate {follow_up} and the context of the interview. The question should be relevant to the candidate's experience and skills. only ask question do not give any context message just ask the question."

    response = groq_client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=150,
        top_p=1,
        stream=False
    )
    # Access the content directly from the first choice
    groq_response = response.choices[0].message.content.strip()
    return groq_response


def generate_score(question, answer):
    """Generate a score for the candidate's answer."""
    prompt = f"Question: {question}\nAnswer: {answer}\n\nEvaluate the answer's accuracy and provide a score out of 5. Explain the score."
    try:
        response = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150,
            top_p=1,
            stream=False
        )
        groq_response = response.choices[0].message.content.strip()
        if "Score:" in groq_response:
            score = int(groq_response.split("Score:")[1].split("/")[0].strip())
            explanation = groq_response.split("Score:")[1].split("\n")[1].strip()
        else:
            score = 0
            explanation = "The answer was not clear enough to assess."
    except:
        return 0, "Error in generating score."
    return score, explanation



def run_interview():
    Greetings = "Hello, welcome to the interview. Let's start with some questions."
    print(Greetings)
    while True:
        question = generate_question(follow_up_questions)
        print(question)
        answer = input("Your answer: ")
        if answer.lower() == "exit":
            break
        score, explanation = generate_score(question, answer)
        print(f"Score: {score}/5")
        print(f"Explanation: {explanation}")
        follow_up_questions[question] = answer



if __name__ == "__main__":
    run_interview()