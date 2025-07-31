import os
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in your .env file.")

client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)
config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True
)

def fetch_airlines(destination: str) -> str:
    return f"🛫 **Airlines to {destination}**\n- Horizon Air: $500 (Luxury)\n- Starlink Flights: $420 (Economy)\n- BudgetWings: $350 (Low-Cost)\n- Travel Duration: 6-10 hours"

def recommend_lodging(destination: str) -> str:
    return f"🛏️ **Lodging in {destination}**\n- Royal Oasis Resort: 5⭐ ($250/night) - Downtown\n- Serenity Suites: 4⭐ ($180/night) - Near Beach\n- Traveler’s Haven: 3⭐ ($60/night) - Budget Option\n- Includes free parking & pool access"

DestinationAgent = Agent(
    name="DestinationAgent",
    instructions="Recommend travel spots based on user’s mood, budget, and preferences. Clarify with questions if needed. Popular: Dubai, New York, Bangkok, Lahore, Cairo."
)

BookingAgent = Agent(
    name="BookingAgent",
    instructions="Simulate arranging airlines and lodging using tools.",
    tools={
        "fetch_airlines": fetch_airlines,
        "recommend_lodging": recommend_lodging
    }
)

ExploreAgent = Agent(
    name="ExploreAgent",
    instructions="Propose local sights, cuisine, and activities for the chosen destination. Highlight iconic landmarks, local dishes, adventures, and travel advice."
)

@cl.on_chat_start
async def start():
    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)
    cl.user_session.set("current_agent", DestinationAgent)
    await cl.Message(content="🌟 **Welcome to Dream Travel AI!** 🌟\n\nI'm your personal travel designer and I'm here to create your perfect adventure! ✈️🌍\n\n**Tell me about yourself:**\n• What's your travel mood? (Adventure, Relaxation, Culture, Food, etc.)\n• What's your budget range? (Luxury, Mid-range, Budget)\n• What interests you most? (History, Nature, Food, Shopping, etc.)\n• Who are you traveling with? (Solo, Couple, Family, Friends)\n\nLet's start planning your dream trip! 🎉").send()

@cl.on_message
async def main(message: cl.Message):
    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": message.content})
    user_input = message.content.lower()

    if any(word in user_input for word in ["book", "hotel", "flight"]):
        agent = BookingAgent
    elif any(word in user_input for word in ["see", "explore", "eat", "do there"]):
        agent = ExploreAgent
    else:
        agent = DestinationAgent

    cl.user_session.set("current_agent", agent)

    msg = cl.Message(content="")
    await msg.send()

    try:
        if agent == BookingAgent:
            destination = None
            for word in ["dubai", "new york", "bangkok", "lahore", "cairo"]:
                if word in user_input:
                    destination = word.title()
                    break

            if destination:
                airlines = fetch_airlines(destination)
                lodging = recommend_lodging(destination)
                await msg.stream_token(f"📍 Your Travel Plan for *{destination}*:\n\n{airlines}\n\n{lodging}")
                history.append({"role": "assistant", "content": msg.content})
                cl.user_session.set("chat_history", history)
                return

        result = Runner.run_streamed(agent, history, run_config=cast(RunConfig, config))
        async for event in result.stream_events():
            if event.type == "raw_response_event" and hasattr(event.data, "delta"):
                await msg.stream_token(event.data.delta)

        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("chat_history", history)

    except Exception as e:
        await msg.stream_token(f"❌ Something went wrong: {str(e)}")