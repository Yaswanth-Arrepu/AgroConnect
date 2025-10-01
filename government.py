from google import genai
import json
import re 
client = genai.Client(api_key="your api key here")
def government(area):  
    try:
        print(f"Fetching government schemes for: {area}")  
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{
                "role": "user",
                "parts": [{
                    "text": f"Provide government schemes for farmers available in {area} from both the central and state governments in simple vocabulary and better explaination. "
                            f"Format the response as a JSON list of dictionaries, where each dictionary contains 'title', 'description', and 'eligibility'. "
                            f"Ensure the response is valid JSON without Markdown formatting."
                }]
            }]
        )
        raw_text = response.text
        cleaned_text = re.sub(r"```json\s*|\s*```", "", raw_text).strip()
        schemes_data = json.loads(cleaned_text)
        if not isinstance(schemes_data, list):
            raise ValueError("API returned invalid format (expected list of dictionaries)")
        return schemes_data  # ✅ Returning data to app.py
    except json.JSONDecodeError:
        print("\n❌ ERROR: Failed to parse JSON. Here is the raw text:")
        print(raw_text)
        return [{"title": "Error", "description": "Invalid JSON format received.", "eligibility": "N/A"}]
    except Exception as e:
        print("\n❌ ERROR OCCURRED:", str(e))
        return [{"title": "Error", "description": str(e), "eligibility": "N/A"}]
