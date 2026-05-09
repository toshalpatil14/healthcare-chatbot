from transformers import pipeline
import re

chatbot = None
try:
    chatbot = pipeline(
        "text2text-generation",
        model="google/flan-t5-small"
    )
except Exception:
    chatbot = None


def _sanitize_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.replace("Possible condition:", "Possible Condition:")
    text = text.replace("Precautions:", "Precautions:")
    text = text.replace("When to see a doctor:", "When to See a Doctor:")
    return text.strip()


def _fallback_response(user_input: str) -> str:
    text = user_input.lower()
    if any(term in text for term in ["chest pain", "shortness of breath", "difficulty breathing"]):
        condition = (
            "Your symptoms may be related to a respiratory infection or irritation. "
            "Chest discomfort or breathing problems should be checked by a healthcare provider."
        )
    elif any(term in text for term in ["fever", "temperature", "chills"]):
        condition = (
            "Your symptoms may be consistent with a viral illness such as a cold or flu. "
            "This often includes fever and body aches."
        )
    elif any(term in text for term in ["cough", "sore throat", "throat pain"]):
        condition = (
            "Your symptoms may be due to a mild respiratory infection or throat irritation."
        )
    elif any(term in text for term in ["nausea", "vomit", "stomach", "diarrhea"]):
        condition = (
            "Your symptoms may be related to a stomach bug, food irritation, or mild digestive upset."
        )
    elif any(term in text for term in ["headache", "migraine", "head pain"]):
        condition = (
            "Your symptoms may be related to tension, dehydration, or a mild viral infection."
        )
    else:
        condition = (
            "Your symptoms may be associated with a common illness such as a cold, mild infection, "
            "or temporary stress-related condition."
        )

    return (
        "Possible Condition:\n"
        f"{condition}\n\n"
        "Precautions:\n"
        "- Stay hydrated\n"
        "- Rest and avoid strenuous activity\n"
        "- Eat nutritious, easy-to-digest foods\n"
        "- Monitor your symptoms regularly\n\n"
        "When to See a Doctor:\n"
        "- If symptoms worsen or persist for several days\n"
        "- High fever does not improve\n"
        "- Trouble breathing, chest pain, or severe discomfort\n"
        "- Confusion, severe headache, or dehydration\n"
    )


def generate_response(user_input: str) -> str:
    prompt = (
        "You are a professional, empathetic healthcare assistant.\n"
        "Read the patient message and answer in this exact format:\n\n"
        "Possible Condition:\n"
        "Precautions:\n"
        "When to See a Doctor:\n\n"
        "Use plain language, be concise, and do not include extra sections.\n"
        "If you are unsure, provide safe general advice and recommend medical evaluation.\n\n"
        f"Patient message:\n{user_input}"
    )

    answer = ""
    if chatbot is not None:
        try:
            result = chatbot(
                prompt,
                max_new_tokens=220,
                do_sample=False,
                return_full_text=False
            )
            answer = result[0].get("generated_text", "").strip()
        except Exception:
            answer = ""

    answer = _sanitize_response(answer)
    if len(answer) < 20 or "Possible Condition:" not in answer:
        answer = _fallback_response(user_input)

    answer = f"{answer}\n\n⚠️ This is not medical advice. Please consult a licensed healthcare professional."
    return answer