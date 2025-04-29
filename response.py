from groq import Groq


groq_client = Groq(api_key='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')
response=groq_client.chat.completions.create(
    model="deepseek-r1-distill-llama-70b",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    temperature=0.5,
    max_tokens=150,
    top_p=1,
    stream=False
)

print(response.choices[0].message.content.strip())