import json
import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
from plyer import notification

app = Flask(__name__)
CORS(app)  # Allows your Chrome Extension to safely pass data to Python

load_dotenv()
# Initialize the Gemini Client
client = genai.Client(api_key = os.getenv("API_KEY"))
print(os.getenv("API_KEY"))

SYSTEM_PROMPT = """
# SYSTEM IDENTITY & OBJECTIVE
You are an advanced Corporate Communication Triage Engine. Your sole purpose is to analyze incoming chat messages from a user's workplace and determine if the message requires an immediate, disruptive desktop notification sound and popup banner. You are a silent backend processor; you must never answer the messages or generate conversational text. Your only job is to evaluate and format data.

# INPUT SPECIFICATION & CONTEXT AWARENESS (Conversational Stream Processing)
1. You will receive data packets extracted directly from live Google Chat streams. 
2. The packet contains the `sender_name` and the `message_text`.
3. Multi-Message Stream Rule: If the incoming payload consists of multiple consecutive messages sent in rapid succession, you must evaluate the collective intent of the whole stream. Even if the first message is low-priority filler (e.g., "Hey"), if any subsequent message contains a critical request, the entire evaluation must be escalated to `is_critical: true`.

# DYNAMIC CONTEXT INGESTION & TARGET ROLES
- VIP Roles: ["CEO", "Manager", "HR"]
- VIP Individual Names: ["Jignesh Ahya", "Dilip Dalsaniya", "Jayesh Tanna", "Punita O", "Gopesh P","Ayushi B"]

## EVALUATION ELEVATION RULE:
If the `sender_name` matches ANY of the names listed in the "VIP Individual Names" array, you must automatically treat that sender with the highest priority and authority status, exactly like a VIP Role.

# CRITICAL PRIORITIZATION RULES (True Conditions)
Set `is_critical` to `true` ONLY when the text contains any of the following intents or explicit triggers:
1. Direct Presence Inquiries: Phrases querying current availability (e.g., "you there?", "are you at your desk?").
2. Summons / Requests to Meet: Explicit directives to gather locally or digitally (e.g., "can you come here for a sec?", "do you have a minute").
3. Unanswered Direct Questions: Any sentence structured as an interrogation or asking for validation/input from the user.
4. Core Task Completion Checks: Messages verifying operational status (e.g., "are you done with the task?").
5. Work/Progress Updates: Requests asking for project updates, delivery statuses, or current workflow timelines.
6. Corporate Announcements: Broad operational changes, organizational news, or event celebrations (e.g., "there will be a celebration today").

# FILTERING & EXCLUSION RULES (False Conditions)
Set `is_critical` to `false` automatically when the incoming text represents routine chatter, including:
1. Status Updates & Breaks: Statements about physical presence or departure (e.g., "going on a break", "out for lunch", "brb", "logging off").
2. Standalone Closures & Acknowledgments: Short, low-context sign-offs, even from leadership (e.g., "done", "good job", "okay", "fine", "noted", "thanks", "ack").
3. Casual Social Banter: Non-work-related casual remarks or morning greetings (e.g., "Good morning team", "Have a great weekend").
4. Automated Bot Noise: Generic calendar reminders or automated server alerts that do not contain a human call-to-action.

# REQUIRED OUTPUT FORMAT
You must output strictly in JSON format. Do not include markdown code blocks (like ```json). Do not include conversational prose.

Expected Structure:
{
  "is_critical": true/false,
  "reasoning": "A 1-sentence analytical breakdown of your decision.",
  "banner_title": "A brief, attention-grabbing header for the notification.",
  "banner_body": "An actionable, condensed summary under 10 words."
}
"""

@app.route('/ping', methods=['GET'])
def ping():
    """Heartbeat route to verify the Extension connection status."""
    print("\n[ EXTENSION LIVE] Extension connected successfully and requested a connection heartbeat check.")
    return jsonify({"status": "online"}), 200

@app.route('/triage', methods=['POST'])
def triage_message():
    data = request.json
    sender = data.get('sender', 'Unknown Sender')
    message = data.get('message', '')

    print("\n" + "="*60)
    print(f"[ INCOMING CHAT] Intercepted message from stream.")
    print(f"   From   : {sender}")
    print(f"   Message: \"{message}\"")
    print("-"*60)

    if not message.strip():
        print("[ SKIPPED] Message contents evaluated as completely empty or unreadable.")
        print("="*60)
        return jsonify({"status": "ignored", "reason": "Empty message"}), 200

    user_content = f"Sender: {sender}\nMessage: {message}"

    try:
        # Requesting Gemini 1.5 Flash with strict JSON formatting enforced
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json"
            ),
        )
        
        ai_result = json.loads(response.text)
        is_critical = ai_result.get('is_critical', False)
        reasoning = ai_result.get('reasoning', 'No explicit breakdown provided.')

        # Print the detailed categorization results directly inside the console
        if is_critical:
            print(f"[ALLOWED ] System evaluation: CRITICAL ALERT INCIDENT.")
            print(f"   Reasoning : {reasoning}")
            print(f"   Pop-up Box: {ai_result.get('banner_title')} -> {ai_result.get('banner_body')}")
            
            # Trigger operating system native banners
            notification.notify(
                title=ai_result.get('banner_title', 'Urgent Workspace Update'),
                message=ai_result.get('banner_body', 'Action required'),
                app_name='Google Chat Triage',
                timeout=8
            )
        else:
            print(f"[BLOCKED ] System evaluation: ROUTINE WORK NOISE.")
            print(f"   Reasoning : {reasoning}")
            print(f"   Action    : Suppressed. Stated pop-up was successfully dropped.")

        print("="*60)
        return jsonify({"status": "success", "result": ai_result}), 200

    except Exception as e:
        print(f"[ API ERROR] Failed to connect or parse payload response: {e}")
        print("="*60)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "#"*60)
    print(" GOOGLE CHAT AI TRIAGE ENGINE IS STARTING...")
    print(" Local Tunnel Interface Listening on Address: [http://127.0.0.1:5000](http://127.0.0.1:5000)")
    print("#"*60 + "\n")
    app.run(port=5000, debug=True)