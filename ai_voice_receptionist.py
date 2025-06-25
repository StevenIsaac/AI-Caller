from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    transcript = request.values.get("SpeechResult", None)

    if transcript:
        completion = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You're a helpful, polite receptionist for a law firm."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_response = completion.choices[0].message["content"]
    else:
        ai_response = "Hi! Thanks for calling. How can I help you today?"

    # Build Twilio voice response
    resp = VoiceResponse()
    gather = Gather(input="speech", action="/voice", method="POST", timeout=5)
    gather.say(ai_response)
    resp.append(gather)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
