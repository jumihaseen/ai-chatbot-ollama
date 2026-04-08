# AI Chatbot (Ollama + Rule-Based Fallback)

A simple Flask web chatbot for **customer-support style** conversations.

- **Primary response source**: a local Ollama LLM (default model: `phi3`)
- **Fallback**: a beginner-friendly **rule-based** response function when Ollama is unavailable or returns an empty/invalid response

This project is designed to run **fully offline** after dependencies and the Ollama model are installed locally.

## How it works

1. The browser UI sends your message to the Flask backend (`POST /chat`).
2. The backend tries to generate a response from Ollama using:
   - `OLLAMA_URL = http://localhost:11434/api/generate`
   - `OLLAMA_MODEL = phi3`
3. If Ollama:
   - cannot be reached (connection/timeout),
   - returns an error,
   - returns **empty output**, or
   - returns **non-JSON / invalid JSON**,
   then the backend replies using `get_rule_based_response(user_message)`.

## Project structure

```
Ai_chatbot_ollama/
  app.py
  README.md
  templates/
    index.html
  static/
    style.css
    script.js
```

- **`app.py`**: Flask server with `/` and `/chat` routes, Ollama call, and rule-based fallback.
- **`templates/index.html`**: Chat page HTML (loads CSS + JS from `/static`).
- **`static/script.js`**: Frontend chat logic (sends messages to `/chat`, renders bubbles).
- **`static/style.css`**: UI styling.

## Requirements

- **Python 3.9+** recommended
- **pip** (Python package manager)
- **Ollama** installed and running locally (optional but recommended)
- Model pulled locally (example: `phi3`)

Python packages used:
- `Flask`
- `requests`

## Setup (Windows)

Open PowerShell in the project folder:

```powershell
cd "C:\Users\HP\Downloads\Ai_chatbot_ollama"
```

Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install flask requests
```

## Ollama setup (offline model)

1. Install Ollama.
2. Pull the model once (requires internet only the first time):

```powershell
ollama pull phi3
```

After the model is pulled, Ollama can run **offline**.

Make sure Ollama is running and listening on `localhost:11434`.

## Run the app

From the project folder:

```powershell
python app.py
```

Then open the URL shown in the terminal (typically):
- `http://127.0.0.1:5000/`

## Using the fallback logic

The fallback activates automatically when Ollama isn’t working.

Examples that the rule-based system handles:
- greetings (“hello”, “hi”)
- order status / tracking
- refunds, returns, delivery time, shipping charges
- cancel order, change address
- payment failed / payment methods
- contact/support hours
- a basic “watches under 10k” browsing guidance message

If a message doesn’t match any rules, it returns a short “Try asking…” help menu.

## Offline vs Internet: what’s actually needed

You do **not** need internet for normal chatting if:
- Flask app is running locally
- Ollama is running locally (for AI answers)
- the model has already been downloaded

You may need internet only for:
- downloading Python packages (`pip install ...`) the first time
- pulling the Ollama model the first time (`ollama pull phi3`)

## Troubleshooting

### “Sorry, I am unable to connect right now.” / connection-style errors

This kind of message is shown when the **browser cannot successfully talk to the Flask server** at `/chat`.

Common causes:
- Flask server is not running
- you opened the HTML file directly instead of visiting `http://127.0.0.1:5000/`
- wrong project folder is running (e.g., you edited `Ai_chatbot_ollama` but started a different `app.py`)
- browser cached an older `static/script.js` (do a hard refresh: **Ctrl+F5**)

Quick checks:
- Visit `http://127.0.0.1:5000/` (not a local file path)
- Restart Flask (`Ctrl+C`, then `python app.py`)
- Hard refresh in the browser (Ctrl+F5)

### Ollama not running / model missing

If Ollama is down, the app should still respond using the **rule-based fallback**.

To use Ollama responses:
- ensure Ollama is running
- ensure the model exists locally:

```powershell
ollama list
```

## Customization

- Change model name in `app.py`:
  - `OLLAMA_MODEL = "phi3"`
- Extend rule-based fallback by adding more keyword rules in:
  - `get_rule_based_response()` in `app.py`

