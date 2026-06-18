from flask import Flask, request, jsonify, send_from_directory
import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', template_folder='.')

# --- Groq client ---
_groq = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)


def _ask_groq(system, prompt):
    """Call Groq API and parse the JSON response."""
    response = _groq.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0,
    )
    content = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    content = re.sub(r'^```(?:json)?\s*', '', content)
    content = re.sub(r'\s*```$', '', content)
    return json.loads(content)


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'home.htm')


# ---------- Groq-powered spell check ----------

@app.route('/api/spellcheck', methods=['POST'])
def spellcheck():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')

    if not isinstance(text, str):
        return jsonify({'error': 'Invalid text payload'}), 400

    try:
        result = _ask_groq(
            "You are a spell checker. Find all misspelled words in the text, "
            "correct them, and produce the refined text. "
            "Do NOT change correct words, proper nouns, emails, phone numbers, "
            "or names of people and places. "
            "Return ONLY a JSON object in this exact format:",
            '{"refined": "the fully corrected text",\n'
            ' "corrections": [{"original": "misspelled", "correction": "fixed"}]}\n\n'
            + text
        )
        return jsonify({
            'refined': result.get('refined', text),
            'corrections': result.get('corrections', []),
            'no_fix': [],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/first-names', methods=['POST'])
def first_names():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    if not isinstance(text, str):
        return jsonify({'error': 'Invalid text payload'}), 400

    try:
        result = _ask_groq(
            "You extract names from text. Return ONLY a JSON object, no extra text.",
            "Extract all person FIRST names from this text. "
            "Ignore place names, common words, greetings, and closings. "
            "Return JSON: {\"first_names\": [\"name1\", \"name2\"]}\n\n" + text
        )
        return jsonify({'first_names': result.get('first_names', [])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/last-names', methods=['POST'])
def last_names():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    if not isinstance(text, str):
        return jsonify({'error': 'Invalid text payload'}), 400

    try:
        result = _ask_groq(
            "You extract names from text. Return ONLY a JSON object, no extra text.",
            "Extract all person LAST names (surnames) from this text. "
            "Ignore place names, common words, greetings, and closings. "
            "Return JSON: {\"last_names\": [\"name1\", \"name2\"]}\n\n" + text
        )
        return jsonify({'last_names': result.get('last_names', [])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)