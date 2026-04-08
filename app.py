from flask import Flask, jsonify, render_template, request
import requests
import string

app = Flask(__name__)

# System prompt that guides the model to behave as customer support.
SYSTEM_PROMPT = (
    "You are a helpful and polite customer support assistant.\n"
    "Answer user queries clearly and professionally.\n"
    "Keep responses short and relevant.\n"
    "If you don't know something, say politely that you will escalate to a human agent."
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"

def get_rule_based_response(user_message: str) -> str:
    """
    Very simple keyword-based chatbot logic.
    This is intentionally beginner-friendly for learning.
    """
    # Normalize text: lowercase + remove punctuation for better keyword matching.
    message = user_message.lower().translate(str.maketrans("", "", string.punctuation))
    words = set(message.split())

    def has_any(*keywords):
        return any(keyword in message for keyword in keywords)

    def has_all_words(*keywords):
        # Checks whether all important words are present in the sentence.
        return all(keyword in words for keyword in keywords)

    # Step 5: Human handoff simulation
    if (
        has_any("not satisfied", "talk to human", "complaint")
        or has_all_words("talk", "human")
    ):
        return "Connecting you to a human agent..."

    # Step 4: Basic customer support responses
    if has_any("hello", "hi", "hey", "good morning", "good evening"):
        return "Hello! Welcome to support. How can I help you today?"
    elif has_all_words("how", "you") and "are" in words:
        return "I am doing well, thank you. How can I assist you with your order?"
    elif has_any("thank you", "thanks", "thx"):
        return "You're welcome! Happy to help."
    elif has_any("bye", "goodbye", "see you"):
        return "Goodbye! Have a great day."
    elif (
        has_any("order status", "track order", "where is my order")
        or has_all_words("order", "status")
        or has_all_words("track", "order")
        or has_all_words("where", "order")
        or has_all_words("when", "order")
        or has_all_words("get", "order")
        or has_all_words("order", "arrive")
        or has_any("when will i get my order", "when will my order arrive")
    ):
        return "You can check your order status in 'My Orders' using your order ID."
    elif (
        has_any("order not received", "late delivery", "delayed")
        or has_all_words("order", "not", "received")
        or has_all_words("late", "delivery")
    ):
        return "Sorry for the delay. Please share your order ID, and we will check it for you."
    elif has_any("refund") or has_all_words("money", "back"):
        return "Refunds are processed within 5-7 business days after approval."
    elif (
        has_any("return policy", "return item", "exchange")
        or has_all_words("return", "policy")
        or has_all_words("return", "item")
    ):
        return "You can return or exchange items within 7 days if they are unused and in original condition."
    elif (
        has_any("delivery time")
        or has_all_words("delivery", "time")
        or has_all_words("how", "long", "delivery")
    ):
        return "Standard delivery usually takes 3-5 business days."
    elif (
        has_any("shipping charge", "shipping cost", "delivery charge")
        or has_all_words("shipping", "cost")
        or has_all_words("shipping", "charge")
    ):
        return "Shipping charges depend on location and are shown at checkout."
    elif (
        has_any("cancel order")
        or has_all_words("cancel", "order")
        or ("cancel" in words and "order" in message)
    ):
        return "You can cancel your order from 'My Orders' before it is shipped."
    elif (
        has_any("change address", "wrong address", "update address")
        or has_all_words("change", "address")
        or has_all_words("update", "address")
    ):
        return "You can update your address before shipment from your account settings."
    elif (
        has_any("payment failed", "payment issue", "transaction failed")
        or has_all_words("payment", "failed")
        or has_all_words("transaction", "failed")
    ):
        return "If payment failed, please retry after a minute or use another payment method."
    elif (
        has_any("payment methods", "how can i pay", "upi", "card", "cash on delivery")
        or has_all_words("payment", "method")
        or "upi" in words
    ):
        return "We support UPI, debit/credit cards, net banking, and cash on delivery in selected areas."
    elif (
        has_any("contact", "phone number", "email support")
        or has_all_words("customer", "care")
        or has_all_words("support", "email")
    ):
        return "You can contact our support team at support@example.com or call +1-234-567-890."
    elif (
        has_any("working hours", "support hours", "when are you available")
        or has_all_words("support", "hours")
        or has_all_words("working", "hours")
    ):
        return "Our support team is available Monday to Saturday, 9:00 AM to 6:00 PM."
    elif (
        has_any("watch", "watches", "new arrivals", "browse products", "catalog")
        or has_all_words("new", "watches")
    ) and (
        has_any("10k", "10000", "under", "below", "range", "budget", "price")
        or "10k" in message.replace(" ", "")
    ):
        return (
            "Open the Watches category on our site or app, then set the price filter "
            "to up to ₹10,000 to see new models in that range. You can sort by “New” or “Latest”."
        )
    elif has_any("watch", "watches") or has_all_words("new", "collection"):
        return (
            "You can explore our Watches section and use filters (price, brand, new arrivals) "
            "to find what you need. If you tell me a budget (e.g. under ₹10,000), I can guide you to the right filter."
        )
    else:
        return (
            "Sorry, I didn't understand that.\n"
            "Try asking:\n"
            "1) What is my order status?\n"
            "2) When will I get my order?\n"
            "3) How long is delivery time?\n"
            "4) Can I cancel my order?\n"
            "5) How do I get a refund?\n"
            "6) What is your return policy?\n"
            "7) My payment failed, what should I do?\n"
            "8) How can I contact support?"
        )


@app.route("/")
def home():
    """Render the main chat page."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Receive user message, send it to Ollama model, and return the model response."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"response": "Please type a message before sending."}), 400

    # Combine system prompt with user message (no rule-based logic).
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nAssistant:"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False,
    }

    try:
        ollama_response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        ollama_response.raise_for_status()
        try:
            result = ollama_response.json()
        except ValueError:
            bot_reply = get_rule_based_response(user_message)
            return jsonify({"response": bot_reply})
        bot_reply = (result.get("response") or "").strip()

        if not bot_reply:
            bot_reply = get_rule_based_response(user_message)

        return jsonify({"response": bot_reply})

    except requests.RequestException:
        return jsonify({"response": get_rule_based_response(user_message)})
    except (ValueError, TypeError):
        return jsonify({"response": get_rule_based_response(user_message)})


if __name__ == "__main__":
    app.run(debug=True)
