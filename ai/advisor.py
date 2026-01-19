from groq import Groq
from config.settings import GROQ_API_KEY

def generate_uidai_plan(topic, data_summary):
    if not GROQ_API_KEY:
        return "⚠️ GROQ API key not configured."

    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
        Role: Senior Strategic Consultant for UIDAI.
        Topic: {topic}
        Data Context: {data_summary}
        Task: Provide a 3-point strategic action plan.
        """
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300
        )
        return completion.choices[0].message.content
    except Exception as e:
        return str(e)
