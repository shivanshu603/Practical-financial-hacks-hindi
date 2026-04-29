import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ContentBrain:
    
    def __init__(self):
        self.history_file = "topics_history.json"
        self.history = self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"used_topics": []}

    def save_history(self, topic):
        if topic and topic not in self.history["used_topics"]:
            self.history["used_topics"].append(topic)
            if len(self.history["used_topics"]) > 200:
                self.history["used_topics"] = self.history["used_topics"][-150:]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)

    def generate_script(self):
        print("💰 Generating Practical Financial Hacks Short...")

        prompt = """
You are a practical Hindi financial advisor and YouTube Shorts creator specializing in "Real Paisa Tips" and "Financial Hacks".

Create ONE highly useful, actionable, and mind-blowing short (45-60 seconds) on money saving hacks, loan repayment strategies, business growth tips, trading knowledge, side income ideas, investment tips, etc.

Rules:
- Script mainly **Hinglish** mein ho (natural spoken Hindi + simple English words)
- Shuruaat strong hook se karo jaise "Yeh hack use karo toh...", "Loan jaldi khatam karna hai toh...", "Business 10x grow karna hai toh..."
- Practical aur real-life actionable advice do (step-by-step)
- End mein ek powerful tip ya sawal ke saath khatam karo
- Topics: Loan repayment, business growth, trading strategies, saving hacks, side hustle, investment, tax saving, etc.

Return ONLY this exact JSON format:

[
  {
    "id": 1,
    "title": "Hinglish catchy SEO title",
    "text": "Full spoken Hinglish script here (45-60 seconds)",
    "visual_1": "cinematic money, business, finance related visuals",
    "visual_2": "satisfying, practical, real-life visual keywords"
  }
]
"""

        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.1-flash"]

        for model_name in models:
            for attempt in range(3):
                try:
                    print(f"🔄 Trying {model_name} (Attempt {attempt+1}/3)")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )

                    clean = response.text.strip().replace("```json", "").replace("```", "").strip()
                    result = json.loads(clean)

                    # Save topic to avoid repetition
                    title = result[0].get("title", "") if isinstance(result, list) else ""
                    if title:
                        self.save_history(title)

                    print(f"✅ SUCCESS with {model_name}")
                    return result[0] if isinstance(result, list) else result

                except Exception as e:
                    err = str(e)
                    print(f"❌ Failed {model_name}: {err[:150]}")
                    if "503" in err or "high demand" in err:
                        time.sleep(10)
                        continue
                    else:
                        break

        print("❌ All models failed.")
        return None


# For testing
if __name__ == "__main__":
    brain = ContentBrain()
    output = brain.generate_script()
    if output:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print("✅ latest_script.json saved")