---
title: agent-profile
app_file: app.py
sdk: gradio
sdk_version: 5.49.1
---
# Agent Profile

This project is a lightweight AI-powered personal profile assistant built using **Gradio** and **OpenAI**.
It represents my professional background and experience and can answer questions about my profile, career, and skills in a conversational way.

The assistant is designed to behave as if you’re directly talking to me on my website.

---

## Live Demo

The app is currently hosted on Hugging Face Spaces:

👉 **[https://huggingface.co/spaces/nagarakesh4/agent-profile](https://huggingface.co/spaces/nagarakesh4/agent-profile)**

You can ask questions there to learn more about my profile, background, experience, and work.

---

## Features

* Conversational AI representing my professional profile
* Uses my Resume PDF and a written summary as context
* Tool-based actions to:

  * Record interest when someone shares their email
  * Log questions the assistant couldn’t answer
* Clean Gradio chat interface
* Simple, minimal runtime setup using `uv`

---

## Who This Is For

- Recruiters or hiring managers exploring my profile
- Engineers curious about how the assistant is built
- Anyone who prefers asking questions instead of reading resumes

---

## Requirements

* Python 3.10+
* `uv`
* OpenAI API key
* Pushover credentials (optional, for notifications)

Environment variables expected:

```bash
OPENAI_API_KEY=...
PUSHOVER_TOKEN=...
PUSHOVER_USER=...
```

---

## Project Structure

```
.
├── app.py
├── summary.txt
├── resume.pdf
├── README.md
└── .env
```

---

## Running Locally

Install dependencies and run the app using `uv`:

```bash
uv run app.py
```

This will start a local Gradio server.

---

## Deploying to Hugging Face Spaces

To deploy using Gradio:

```bash
uv run gradio deploy
```

Once deployed, the app will be accessible via your Hugging Face Space.

---

## How It Works (High Level)

* Loads my profile data from:

  * `summary.txt`
  * `resume.pdf`
* Builds a system prompt that instructs the AI to stay in character
* Uses OpenAI function calling for structured actions
* Runs a loop that executes tools when required and continues the conversation
* Exposes everything via a Gradio chat interface

---

## Notes

* If the assistant doesn’t know the answer to a question, it records the question for review.
* If a user shows interest in getting in touch, it prompts for an email and records it.
* The app is intentionally simple and focused on clarity and correctness over complexity.

---

If you’d like to explore the code or ask questions about my background, feel free to try the live version linked above.
