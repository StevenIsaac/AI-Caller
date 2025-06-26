from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

conversation_history = [
    {"role": "system", "content": "You're a helpful, polite receptionist for a law firm."}
]

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()

    speech = request.values.get("SpeechResult", "").strip()
    print("Caller said:", speech)

    if speech:
        conversation_history.append({"role": "user", "content": speech})
        ai_response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=conversation_history
        )
        reply = ai_response.choices[0].message["content"]
        conversation_history.append({"role": "assistant", "content": reply})
    else:
        reply = "Hi! Thanks for calling. How can I help you today?"

    gather = Gather(
        input="speech",
        action="/voice",
        method="POST",
        timeout=6,
        speechTimeout="auto"
    )
    gather.say(reply)
    resp.append(gather)

    resp.redirect("/voice")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)