from flask import Flask, request
import requests

app = Flask(__name__)

# Энийг дараа нь жинхэнэ утгаар нь солино
VERIFY_TOKEN = "eegii_token"
PAGE_ACCESS_TOKEN = "PAGE_TOKEN_OY_BELEN_BOLHOD_END_TAVINA"


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return challenge, 200
    else:
        return "Verification token mismatch", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Got data:", data)

    if "entry" in data:
        for entry in data["entry"]:
            for event in entry.get("messaging", []):
                sender_id = event["sender"]["id"]

                if "message" in event and "text" in event["message"]:
                    user_text = event["message"]["text"]
                    reply_text = generate_reply(user_text)
                    send_message(sender_id, reply_text)

    return "EVENT_RECEIVED", 200


def generate_reply(text: str) -> str:
    t = text.lower()

    if "сайн" in t or "hello" in t or "hi" in t:
        return "Сайн байна уу 😊 Танд яаж туслах вэ?"

    if "үнэ" in t or "price" in t:
        return "Манай үйлчилгээний үнэ: \n- Үйлчилгээ A: 20,000₮\n- Үйлчилгээ B: 35,000₮"

    if "байршил" in t or "where" in t or "location" in t:
        return "Манай байршил: Улаанбаатар хот, ..."

    if "цага" in t or "цагийн хуваарь" in t or "time" in t:
        return "Манай ажиллах цаг: Даваа–Ням 10:00–20:00."

    return "Таны мессежийг хүлээж авлаа. Удахгүй админ хариу өгөх болно 😊"


def send_message(recipient_id: str, message_text: str):
    url = "https://graph.facebook.com/v19.0/me/messages"

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    response = requests.post(url, params=params, json=data)

    if response.status_code != 200:
        print("Error sending message:", response.status_code, response.text)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
