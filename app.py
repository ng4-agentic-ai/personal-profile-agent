from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import requests
from pypdf import PdfReader
import gradio as gr


# -------------------------------------------------------------------
# Environment setup
# -------------------------------------------------------------------

load_dotenv(override=True)


# -------------------------------------------------------------------
# Notification helpers
# -------------------------------------------------------------------

def send_notification(message: str):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": message,
        }
    )

def init_user(prompt):
    send_notification(
        f"A user started using your huggingface profile chat. This uses OpenAI keys, know the limits! Their prompt is "
        + prompt
    )
    return { "status" : "done"}

def save_contact_interest(email, name="Name not provided", notes="not provided"):
    send_notification(
        f"Interested User: {name} with email {email} and notes {notes}"
    )
    return {"recorded": "ok"}


def log_unanswered_query(question):
    send_notification(
        f"Question: {question} asked that I couldn't answer"
    )
    return {"recorded": "ok"}


# -------------------------------------------------------------------
# Tool schemas (unchanged semantics)
# -------------------------------------------------------------------

CONTACT_TOOL_SCHEMA = {
    "name": "save_contact_interest",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

UNKNOWN_QUESTION_SCHEMA = {
    "name": "log_unanswered_query",
    "description": "Always use this tool to record any question that couldn't be answered",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            }
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

REGISTERED_TOOLS = [
    {"type": "function", "function": CONTACT_TOOL_SCHEMA},
    {"type": "function", "function": UNKNOWN_QUESTION_SCHEMA},
]


# -------------------------------------------------------------------
# Core chatbot engine
# -------------------------------------------------------------------

class PersonalProfileAgent:

    def __init__(self):
        self.client = OpenAI()
        self.identity = "Venkata Buddhiraju"
        self.linkedin_text = self._load_linkedin_pdf("./resume.pdf")

    # -----------------------------
    # Data loading
    # -----------------------------

    def _load_linkedin_pdf(self, path: str) -> str:
        reader = PdfReader(path)
        combined_text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                combined_text += extracted
        return combined_text

    # -----------------------------
    # Prompt construction
    # -----------------------------

    def build_system_prompt(self) -> str:
        return (
            f"You are acting as {self.identity}. You are answering questions on "
            f"{self.identity}'s website, particularly questions related to career, "
            f"background, skills, and experience.\n\n"
            f"Behave professionally and engagingly, as if speaking to a potential "
            f"client or employer.\n\n"
            f"If you do not know the answer to a question, you MUST use the "
            f"log_unanswered_query tool.\n\n"
            f"If the conversation continues, try to guide the user toward sharing "
            f"their email and record it using save_contact_interest.\n\n"
            f"## LinkedIn Profile:\n{self.linkedin_text}\n\n"
            f"Always stay in character as {self.identity}."
        )

    # -----------------------------
    # Tool execution
    # -----------------------------

    def _execute_tools(self, tool_calls):
        tool_responses = []

        for call in tool_calls:
            function_name = call.function.name
            arguments = json.loads(call.function.arguments)

            print(f"Invoking tool: {function_name}", flush=True)

            tool_fn = globals().get(function_name)
            result = tool_fn(**arguments) if tool_fn else {}

            tool_responses.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result)
            })

        return tool_responses

    # -----------------------------
    # Chat handler (Gradio entry)
    # -----------------------------

    def respond(self, user_input, conversation_history):
        if len(conversation_history) > 25:
            return "This session has reached its limit. Please refresh."

        if len(user_input) > 2000:
            return "Input characters should be less than 2000"
        
        init_user(
            f"{user_input}. - Total Conversation History: {len(conversation_history)}"
        )

        dialogue = (
            [{"role": "system", "content": self.build_system_prompt()}]
            + conversation_history
            + [{"role": "user", "content": user_input}]
        )

        while True:
            completion = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=dialogue,
                tools=REGISTERED_TOOLS
            )

            choice = completion.choices[0]

            if choice.finish_reason == "tool_calls":
                assistant_msg = choice.message
                dialogue.append(assistant_msg)
                dialogue.extend(self._execute_tools(assistant_msg.tool_calls))
            else:
                return choice.message.content


# -------------------------------------------------------------------
# App bootstrap
# -------------------------------------------------------------------

if __name__ == "__main__":
    agent = PersonalProfileAgent()
    gr.ChatInterface(agent.respond, type="messages").launch()
