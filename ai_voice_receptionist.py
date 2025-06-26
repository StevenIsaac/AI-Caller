from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversation_history = [
    {"role": "system", "content": "You're a helpful, polite receptionist for a law firm."}
]

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()

    speech = request.values.get("SpeechResult", "").strip()
    logger.info(f"Caller said: {speech}")

    try:
        if speech:
            conversation_history.append({"role": "user", "content": speech})

            chat_completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=conversation_history
            )

            reply = chat_completion.choices[0].message.content

            conversation_history.append({"role": "assistant", "content": reply})
            logger.info(f"AI response: {reply}")
        else:
            reply = "Hi! Thanks for calling. How can I help you today?"
            logger.info("No speech received. Playing initial greeting.")

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

    except Exception as e:
        logger.error(f"Error during voice handling: {e}")
        resp.say("Sorry, something went wrong. Please try again later.")
        return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
