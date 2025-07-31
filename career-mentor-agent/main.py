import os
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
from career_agent import CareerMentorAgent, career_agent

# Load environment variables
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

@cl.on_chat_start
async def start():
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )
    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)
    cl.user_session.set("current_field", None)
    agent: CareerMentorAgent = CareerMentorAgent(name="Assistant", instructions="You are a helpful assistant", model=model)
    cl.user_session.set("agent", agent)
    print(f"Runner class loaded: {Runner}")
    await cl.Message(content="👋 Welcome to the Career Mentor Agent! I'm here to help you explore career opportunities and guide you through different professional fields.").send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="Thinking...")
    await msg.send()
    agent: CareerMentorAgent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []
    session = cl.user_session
    history.append({"role": "user", "content": message.content})
    try:
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
        response_content, _ = agent.respond(history, session)
        msg.content = response_content
        await msg.update()
        cl.user_session.set("chat_history", history + [{"role": "assistant", "content": response_content}])
        print(f"User: {message.content}")
        print(f"Assistant: {response_content}")
    except Exception as e:
        msg.content = "I apologize, but I encountered an error. Please try again or rephrase your question."
        await msg.update() 