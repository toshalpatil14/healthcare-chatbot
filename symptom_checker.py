from openai import OpenAI
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ✅ Get your FREE API key at: https://platform.openai.com/
# New accounts get $5 free credits — enough for thousands of chatbot messages
# Set environment variable: OPENAI_API_KEY=your_key_here

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """You are a warm, empathetic, and knowledgeable healthcare assistant helping patients understand their symptoms.

When a patient describes symptoms, ALWAYS respond in this EXACT format (use the emojis and headings as shown):

🩺 Possible Condition:
[2-3 sentences explaining the most likely condition(s) in simple, friendly language. Be specific to their symptoms.]

💊 Precautions:
- [Specific precaution tailored to their exact symptoms]
- [Another relevant precaution]
- [Another relevant precaution]
- [Another relevant precaution]

🩹 Home Remedies & Care Tips:
- [A practical home remedy specific to their symptoms]
- [Another helpful tip]
- [Another helpful tip]

🚨 When to See a Doctor Immediately:
- [A specific red flag related to their symptoms]
- [Another warning sign]
- [Another warning sign]

💙 Encouragement:
[1-2 warm, reassuring sentences to comfort the patient and motivate them to take care.]

STRICT RULES:
- Every response MUST be unique and tailored — never repeat the same advice for different symptoms
- Use plain, friendly language — explain any medical terms you use
- Always say "may be" or "could indicate" — never give a definitive diagnosis
- Be compassionate, never alarming
- Precautions and remedies must match the specific symptom described
"""


def _fallback_response(user_input: str) -> str:
    """Keyword-based fallback if API is unavailable."""
    text = user_input.lower()

    if any(t in text for t in ["chest pain", "shortness of breath", "difficulty breathing"]):
        condition = "a respiratory infection or possible cardiac irritation"
        precautions = [
            "Sit upright and stay calm — lying flat can worsen breathing difficulty",
            "Avoid any physical exertion until symptoms subside",
            "Loosen tight clothing around your chest",
            "Monitor your oxygen levels if you have a pulse oximeter",
        ]
        remedies = [
            "Inhale steam from a bowl of hot water (keep safe distance) to ease breathing",
            "Drink warm ginger or tulsi tea to soothe the airways",
            "Practice slow, deep belly breathing to reduce anxiety",
        ]
        red_flags = [
            "Chest pain radiates to your arm, jaw, or back",
            "You feel dizzy, faint, or break into a cold sweat",
            "Lips or fingertips turn bluish",
        ]
        cheer = "Breathing difficulties can feel scary, but you're being smart by paying attention. Stay calm — most respiratory issues are manageable with proper care."

    elif any(t in text for t in ["fever", "temperature", "chills"]):
        condition = "a viral illness such as influenza or a common cold"
        precautions = [
            "Drink at least 8-10 glasses of water or ORS to prevent dehydration",
            "Take paracetamol (Calpol/Crocin) to bring down the fever",
            "Rest in a well-ventilated room — avoid AC/fan blowing directly on you",
            "Wear light, breathable clothing",
        ]
        remedies = [
            "Apply a cool, damp cloth on your forehead and wrists",
            "Drink warm turmeric milk (haldi doodh) before bed",
            "Eat light foods like khichdi, dal rice, or clear soup",
        ]
        red_flags = [
            "Fever crosses 103°F (39.4°C) and does not come down with medication",
            "Fever lasts more than 3 days continuously",
            "You develop a stiff neck, severe headache, or rash alongside fever",
        ]
        cheer = "Fevers are your body's way of fighting infection — you're stronger than you think! With rest and hydration, most fevers resolve within a couple of days."

    elif any(t in text for t in ["cough", "sore throat", "throat pain"]):
        condition = "a mild upper respiratory tract infection or throat irritation"
        precautions = [
            "Gargle with warm salt water (1/2 tsp salt in a glass) 3-4 times daily",
            "Avoid cold drinks, ice cream, and refrigerated foods completely",
            "Stay away from dusty or smoky environments",
            "Speak less to rest your vocal cords if your throat is inflamed",
        ]
        remedies = [
            "Drink warm honey-lemon tea — honey coats the throat and has antibacterial properties",
            "Suck on ginger candy or chew a small piece of raw ginger with honey",
            "Inhale steam with a few drops of eucalyptus oil for nasal and throat relief",
        ]
        red_flags = [
            "You develop high fever (above 101°F) alongside throat pain",
            "White patches or pus visible on your tonsils",
            "Difficulty swallowing liquids or saliva",
        ]
        cheer = "A sore throat is uncomfortable but very treatable at home! Warm fluids and rest are your best friends right now — you'll feel better soon."

    elif any(t in text for t in ["nausea", "vomit", "stomach", "diarrhea"]):
        condition = "a stomach infection, food irritation, or gastroenteritis"
        precautions = [
            "Sip small amounts of water or ORS every 10-15 minutes — don't gulp",
            "Avoid solid food for the first few hours; introduce plain foods gradually",
            "Stay away from dairy, spicy, fried, or oily foods until fully recovered",
            "Wash hands thoroughly after every toilet visit",
        ]
        remedies = [
            "Drink jeera (cumin) water — boil 1 tsp cumin in 2 cups water, sip warm",
            "Eat plain rice with a pinch of salt — it helps bind loose stools",
            "Ginger tea with a pinch of black salt helps settle nausea",
        ]
        red_flags = [
            "Blood in vomit or stool",
            "Severe abdominal pain that doesn't ease",
            "Signs of dehydration: no urination for 6+ hours, dry mouth, sunken eyes",
        ]
        cheer = "Stomach troubles are no fun, but your body is working hard to flush out what's bothering it. Stay patient, stay hydrated, and you'll feel lighter soon!"

    elif any(t in text for t in ["headache", "migraine", "head pain"]):
        condition = "a tension headache, dehydration, or a mild viral infection"
        precautions = [
            "Drink 2-3 glasses of water immediately — dehydration is the #1 cause of headaches",
            "Step away from screens and rest your eyes in a dark, quiet room",
            "Avoid loud music, bright lights, and strong smells",
            "Skip caffeine if you're prone to migraines — it can worsen rebound headaches",
        ]
        remedies = [
            "Apply a cold pack or ice wrapped in cloth on your forehead for 15 minutes",
            "Gently massage your temples, neck, and shoulders in circular motions",
            "Peppermint oil applied to temples can relieve tension headaches naturally",
        ]
        red_flags = [
            "Sudden, extremely severe headache described as 'the worst of your life'",
            "Headache with fever, stiff neck, or light sensitivity",
            "Headache after a head injury or fall",
        ]
        cheer = "Headaches are one of the most common ailments — and also one of the most responsive to simple care. A little rest, water, and calm will go a long way!"

    else:
        condition = "a common illness, fatigue, or stress-related condition"
        precautions = [
            "Get 7-9 hours of quality sleep — your body heals most during sleep",
            "Drink at least 8 glasses of water throughout the day",
            "Eat small, nutritious meals — avoid skipping meals",
            "Reduce screen time and take short breaks every hour",
        ]
        remedies = [
            "Drink warm herbal tea (chamomile, ginger, or tulsi) to relax and soothe",
            "Take a 10-minute walk in fresh air — gentle movement boosts immunity",
            "Practice 5 minutes of deep breathing or light stretching",
        ]
        red_flags = [
            "Symptoms worsen or new symptoms appear within 24-48 hours",
            "You feel confused, extremely weak, or unable to perform daily tasks",
            "Any symptom that persists beyond 3-5 days without improvement",
        ]
        cheer = "Taking care of your health is always the right move. Be kind to yourself, rest well, and don't hesitate to seek professional help if things don't improve."

    return (
        f"🩺 Possible Condition:\n"
        f"Your symptoms may be related to {condition}. This assessment is based on common patterns — individual cases can vary.\n\n"
        f"💊 Precautions:\n" + "\n".join(f"- {p}" for p in precautions) + "\n\n"
        f"🩹 Home Remedies & Care Tips:\n" + "\n".join(f"- {r}" for r in remedies) + "\n\n"
        f"🚨 When to See a Doctor Immediately:\n" + "\n".join(f"- {f}" for f in red_flags) + "\n\n"
        f"💙 Encouragement:\n{cheer}"
    )


def generate_response(user_input: str) -> str:
    """
    Generate a high-quality, varied healthcare response using OpenAI GPT-3.5-turbo.
    Falls back to keyword-based response if API is unavailable.
    """
    answer = ""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",   # Free-tier friendly; swap to "gpt-4o-mini" for even better quality
            max_tokens=600,
            temperature=0.8,         # Higher = more varied and natural responses every time
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"I'm experiencing the following symptoms: {user_input}"}
            ]
        )
        answer = response.choices[0].message.content.strip()

    except Exception as e:
        error_msg = str(e).lower()
        if "auth" in error_msg or "api key" in error_msg or "invalid" in error_msg:
            print("[ERROR] Invalid or missing API key. Set OPENAI_API_KEY environment variable.")
        elif "rate" in error_msg or "quota" in error_msg:
            print("[ERROR] API quota exceeded. Using fallback response.")
        else:
            print(f"[ERROR] OpenAI API call failed: {e}")
        answer = _fallback_response(user_input)

    # Validate response has the expected structure; use fallback if malformed
    if len(answer) < 30 or "Possible Condition" not in answer:
        answer = _fallback_response(user_input)

    disclaimer = "\n\n⚠️ This is not medical advice. Please consult a licensed healthcare professional for proper diagnosis and treatment."
    return answer + disclaimer