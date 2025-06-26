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
    try:
        transcript = request.values.get("SpeechResult", None)
        print(f"Transcript received: {transcript}")

        if transcript:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI receptionist."},
                    {"role": "user", "content": transcript}
                ]
            )
            ai_reply = response.choices[0].message["content"]
        else:
            ai_reply = "Hi! Thanks for calling. How can I help you today?"

        print(f"AI reply: {ai_reply}")

        twiml = VoiceResponse()
        gather = Gather(input="speech", timeout=3, action="/voice", method="POST")
        gather.say(ai_reply)
        twiml.append(gather)
        return str(twiml)

    except Exception as e:
        print("ERROR:", e)
        return str(VoiceResponse().say("Sorry, something went wrong. Please try again later."))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
