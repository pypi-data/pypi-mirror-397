"""Slack bot powered by PraisonAI."""

import os
import asyncio
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_praisonai_bot.client import PraisonAIClient


def create_app(bot_token: str, api_url: str = "http://localhost:8080", timeout: int = 300) -> App:
    """Create and configure the Slack app."""
    app = App(token=bot_token)
    praisonai = PraisonAIClient(api_url=api_url, timeout=timeout)

    @app.command("/ask")
    def handle_ask(ack, respond, command):
        ack()
        query = command.get("text", "")
        if not query:
            respond("Usage: /ask <your question>")
            return
        respond("🔄 Processing your request...")
        try:
            result = asyncio.run(praisonai.run_workflow(query))
            respond(result or "No response received.")
        except Exception as e:
            respond(f"❌ Error: {str(e)}")

    @app.command("/agent")
    def handle_agent(ack, respond, command):
        ack()
        parts = command.get("text", "").split(maxsplit=1)
        if len(parts) < 2:
            respond("Usage: /agent <agent_name> <your question>")
            return
        agent, query = parts[0], parts[1]
        respond(f"🔄 Asking {agent} agent...")
        try:
            result = asyncio.run(praisonai.run_agent(query, agent))
            respond(result or "No response received.")
        except Exception as e:
            respond(f"❌ Error: {str(e)}")

    @app.command("/agents")
    def handle_agents(ack, respond):
        ack()
        try:
            result = asyncio.run(praisonai.list_agents())
            respond(f"*Available PraisonAI Agents:*\n{result}")
        except Exception as e:
            respond(f"❌ Error: {str(e)}")

    @app.event("app_mention")
    def handle_mention(event, say):
        text = event.get("text", "")
        # Remove the bot mention from the text
        query = " ".join(text.split()[1:]) if text else ""
        if not query:
            say("Hi! Mention me with a question and I'll use PraisonAI to help you.")
            return
        say("🔄 Processing your request...")
        try:
            result = asyncio.run(praisonai.run_workflow(query))
            say(result or "No response received.")
        except Exception as e:
            say(f"❌ Error: {str(e)}")

    return app


def main():
    """Main entry point."""
    load_dotenv()

    bot_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    api_url = os.getenv("PRAISONAI_API_URL", "http://localhost:8080")
    timeout = int(os.getenv("PRAISONAI_TIMEOUT", "300"))

    if not bot_token or not app_token:
        print("❌ Error: SLACK_BOT_TOKEN and SLACK_APP_TOKEN are required")
        print("Set them in .env file or environment")
        return

    app = create_app(bot_token, api_url, timeout)
    handler = SocketModeHandler(app, app_token)
    print("✅ PraisonAI Slack Bot started!")
    print(f"📡 Connected to PraisonAI at {api_url}")
    handler.start()


if __name__ == "__main__":
    main()
