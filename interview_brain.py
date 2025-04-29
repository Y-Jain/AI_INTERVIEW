import json
from groq import Groq
import re

class InterviewBrain:
    def __init__(self, api_key, model_config):
        self.groq_client = Groq(api_key=api_key)
        self.model_config = model_config
        self.follow_up_questions = {}

    def get_resume_parsed_data(self):
        """Parse the resume text and extract relevant information."""
        # Placeholder function to parse resume text
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

    def generate_question(self, follow_up=None):
        if follow_up is None:
            follow_up = {}
        prompt = (
            f"Generate the question based on the resume data: {self.get_resume_parsed_data()} "
            f"and the previous question and response of the candidate {follow_up} and the context of the interview. "
            f"The question should be relevant to the candidate's experience and skills. "
            f"Only ask the question, do not give content of <think> tag."
        )
        response = self.groq_client.chat.completions.create(
            model=self.model_config["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=self.model_config["temperature"],
            max_tokens=self.model_config["max_tokens"],
            top_p=self.model_config["top_p"],
            stream=self.model_config["stream"]
        )
        return response.choices[0].message.content.strip()

    def generate_score(self, question, answer):
        """Generate a score for the candidate's answer."""
        prompt = (
            f"Question: {question}\nAnswer: {answer}\n\n"
            f"Evaluate the answer's accuracy and provide a single score out of 5. "
            f"Only return the score in the format 'Score: X' followed by an explanation."
        )
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model_config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.model_config["temperature"],
                max_tokens=self.model_config["max_tokens"],
                top_p=self.model_config["top_p"],
                stream=self.model_config["stream"]
            )
            groq_response = response.choices[0].message.content.strip()
            
            # Extract score and explanation
            score = 0
            explanation = "The answer was not clear enough to assess."
            score_match = re.search(r'\bScore:\s*(\d+)', groq_response, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
                explanation_start = groq_response.find("Explanation:")
                explanation = groq_response[explanation_start:].strip() if explanation_start != -1 else groq_response
            else:
                explanation = groq_response  # Use the entire response if no "Score:" found
        except Exception as e:
            return 0, f"Error in generating score: {str(e)}"
        
        return score, explanation

    def run_interview(self):
        """Run the interview process."""
        print("Hello, welcome to the interview. Let's start with some questions.")
        while True:
            question = self.generate_question(self.follow_up_questions)
            print(question)
            answer = input("Your answer: ")
            if answer.lower() == "exit":
                break
            score, explanation = self.generate_score(question, answer)
            print(f"Score: {score}/5")
            print(f"Explanation: {explanation}")
            self.follow_up_questions[question] = answer




# obj=InterviewBrain(api_key = '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',
# model_config = {
#     "model": "llama-3.1-8b-instant",
#     "temperature": 0.5,
#     "max_tokens": 150,
#     "top_p": 1,
#     "stream": False
# })
# obj.run_interview()