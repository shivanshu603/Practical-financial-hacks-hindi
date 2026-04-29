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
            except Exception:
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

        used = self.history.get("used_topics", [])[-20:]
        used_str = ", ".join(used) if used else "none"

        prompt = f"""
You are a practical Hindi financial advisor and YouTube Shorts creator specializing in "Real Paisa Tips" and "Financial Hacks".

Create ONE highly useful, actionable, and mind-blowing short (45-60 seconds) on money saving hacks, loan repayment strategies, business growth tips, trading knowledge, side income ideas, investment tips, etc.

Rules:
- Script mainly Hinglish mein ho (natural spoken Hindi + simple English words)
- Shuruaat strong hook se karo jaise "Yeh hack use karo toh...", "Loan jaldi khatam karna hai toh...", "Business 10x grow karna hai toh..."
- Practical aur real-life actionable advice do (step-by-step)
- End mein ek powerful tip ya sawal ke saath khatam karo
- Topics: Loan repayment, business growth, trading strategies, saving hacks, side hustle, investment, tax saving, etc.
- Do NOT repeat these recently used topics: {used_str}

VISUAL KEYWORD RULES:
- visual_1 and visual_2 are Pexels.com stock video search terms
- Must be 3-4 plain English words describing something REAL and FILMABLE
- Must match the script topic visually
- NO abstract words like "cinematic", "satisfying", "ASMR", "dramatic"
- NO Hindi words

Examples:
  Loan topic     -> "person signing loan document"  /  "bank building exterior"
  Saving money   -> "piggy bank coins saving"       /  "person counting cash money"
  Investment     -> "stock market graph screen"     /  "person laptop finance"
  Business       -> "small business owner shop"     /  "entrepreneur office meeting"
  Trading        -> "stock trading screen charts"   /  "financial data monitor"

Return ONLY valid JSON, no extra text:

[
  {{
    "id": 1,
    "title": "Hinglish catchy SEO title under 60 characters",
    "text": "Full spoken Hinglish script (45-60 seconds when read aloud)",
    "hook_text": "Short bold on-screen hook line in Hinglish (4-6 words)",
    "visual_1": "3-4 word english pexels search term matching script topic",
    "visual_2": "3-4 word english pexels search term different angle same topic"
  }}
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

                    # Ensure result is always a list
                    if isinstance(result, dict):
                        result = [result]

                    title = result[0].get("title", "") if isinstance(result, list) else ""
                    if title:
                        self.save_history(title)

                    print(f"✅ SUCCESS with {model_name}")
                    print(f"   📽️  visual_1 → '{result[0].get('visual_1')}'")
                    print(f"   📽️  visual_2 → '{result[0].get('visual_2')}'")

                    return result   # ← Always list return karo

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


if __name__ == "__main__":
    brain = ContentBrain()
    output = brain.generate_script()
    if output:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print("✅ latest_script.json saved")
