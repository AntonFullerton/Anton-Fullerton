#!/usr/bin/env python3
"""
Punch the Monkey News Tracker - Web App
"""

import os
from flask import Flask, render_template, request, jsonify, session
import anthropic

app = Flask(__name__)
app.secret_key = os.urandom(24)

SYSTEM_PROMPT = """You are a knowledgeable assistant who specialises in tracking
news and updates about Punch the Monkey — the real animal, NOT anything to do
with cryptocurrency, blockchain, or "Punch The Monkey" crypto tokens.

When asked for updates about Punch the Monkey, provide:
1. Notable press coverage or media mentions
2. Any significant events or milestones
3. Current known status/welfare if available
4. Where people can follow his latest news (e.g. sanctuary/zoo social pages)

Be specific about dates where known. If you are unsure of very recent news,
state that clearly. Keep responses concise, factual, and well-structured using
markdown. Always clarify which specific Punch the Monkey you are referring to
(e.g. a sanctuary animal, a zoo animal, a media-famous primate, etc.)."""

INITIAL_QUERY = """Give me a full briefing on Punch the Monkey. I want:
- Who he is and where he lives/lived
- Any notable press coverage or media stories about him
- Recent news or updates about his condition and welfare
- Where I can follow ongoing updates about him
- Anything else noteworthy about him

Do not include anything about cryptocurrency. Focus entirely on the animal."""


def get_client():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return None
    return anthropic.Anthropic(api_key=key)


@app.route("/")
def index():
    session["history"] = []
    return render_template("index.html")


@app.route("/briefing", methods=["POST"])
def briefing():
    client = get_client()
    if not client:
        return jsonify({"error": "ANTHROPIC_API_KEY not set"}), 500

    history = [{"role": "user", "content": INITIAL_QUERY}]
    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=history,
        )
    except anthropic.APIError as e:
        return jsonify({"error": str(e)}), 500

    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    session["history"] = history
    return jsonify({"reply": reply, "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens})


@app.route("/chat", methods=["POST"])
def chat():
    client = get_client()
    if not client:
        return jsonify({"error": "ANTHROPIC_API_KEY not set"}), 500

    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    history = session.get("history", [])
    history.append({"role": "user", "content": user_message})

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )
    except anthropic.APIError as e:
        return jsonify({"error": str(e)}), 500

    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    session["history"] = history
    return jsonify({"reply": reply, "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
