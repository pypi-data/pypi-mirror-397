"""Example Chainlit app with PraisonAI integration."""

import chainlit as cl
from chainlit_praisonai.client import PraisonAIClient

# Initialize client
client = PraisonAIClient()


@cl.on_chat_start
async def start():
    """Called when a new chat session starts."""
    await cl.Message(
        content="👋 Welcome! I'm powered by PraisonAI multi-agent framework. How can I help you?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    # Show thinking indicator
    msg = cl.Message(content="")
    await msg.send()

    try:
        # Get response from PraisonAI
        response = await client.run_workflow(message.content)
        msg.content = response
        await msg.update()
    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()
