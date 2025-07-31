import os
from dotenv import load_dotenv
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
try:
    from agents.run import RunConfig
except ImportError:
    RunConfig = None  # Fallback if RunConfig is not available
import random

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY is not set in your .env file.")

client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Mystery Treasure Hunt"
    }
)

# Set Gemini model
model = OpenAIChatCompletionsModel(
    model="mistralai/mistral-7b-instruct:free",
    openai_client=client
)

def roll_dice(sides: int = 6) -> str:
    result = random.randint(1, sides)
    return f"🎲 You rolled a {result} on a {sides}-sided die!"

def create_event(player_action: str) -> str:
    events = [
        "You find a dusty map hidden behind a bookshelf!",
        "A locked chest glints in the corner of the room.",
        "A creaky floorboard reveals a secret compartment!",
        "You hear footsteps approaching from the shadows.",
        "A stray cat drops a shiny key at your feet."
    ]
    return f"🔔 **Event**: {random.choice(events)}"

NarratorAgent = Agent(
    name="NarratorAgent",
    instructions="Guide a mystery treasure hunt in a small town. Describe simple scenes (e.g., old library, town square) and prompt player actions (e.g., search, move, inspect). Use events when relevant.",
    model=model
)

MonsterAgent = Agent(
    name="MonsterAgent",
    instructions="Handle obstacles like traps or guards. Use roll_dice to decide outcomes (e.g., evade a trap, sneak past a guard). Keep it simple and non-fantasy (no dragons).",
    tools={"roll_dice": roll_dice},
    model=model
)

ItemAgent = Agent(
    name="ItemAgent",
    instructions="Manage player items and rewards (e.g., keys, maps, coins). Use create_event to introduce items or challenges. Keep items everyday and practical.",
    tools={"create_event": create_event},
    model=model
)

@cl.on_chat_start
async def start():
    cl.user_session.set("chat_history", [])
    cl.user_session.set("current_agent", NarratorAgent)
    await cl.Message(content="🕵️ **Welcome to the Mystery Treasure Hunt!** 🕵️\n\nYou're in the quiet town of Willow Creek, chasing clues to a hidden treasure. You start in the town square, with an old fountain and a dusty library nearby.\n\n**Tell me about yourself:**\n• What's your adventurer style? (Curious Explorer, Clever Detective, etc.)\n• What's your goal? (Find treasure, solve the mystery, etc.)\n• What's your first move? (Search, explore, talk to locals, etc.)\n\nLet’s uncover the secrets of Willow Creek! 🔍").send()

@cl.on_message
async def main(message: cl.Message):
    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": message.content})
    user_input = message.content.lower()

    if any(word in user_input for word in ["trap", "guard", "obstacle", "sneak", "evade"]):
        agent = MonsterAgent
    elif any(word in user_input for word in ["item", "find", "treasure", "key", "map"]):
        agent = ItemAgent
    else:
        agent = NarratorAgent

    cl.user_session.set("current_agent", agent)

    msg = cl.Message(content="")
    await msg.send()

    try:
        if agent == MonsterAgent:
            obstacle = random.choice(["creaky trapdoor", "nosy guard", "locked gate"])
            if "sneak" in user_input or "evade" in user_input:
                dice_result = roll_dice(10)
                await msg.stream_token(f"🚨 **Challenge: {obstacle.title()}**:\n\n{dice_result}\n\nYou try to slip past the obstacle. Your success depends on the roll...")
                history.append({"role": "assistant", "content": msg.content})
                cl.user_session.set("chat_history", history)
                return

        if agent == ItemAgent:
            event = create_event(user_input)
            await msg.stream_token(f"🎁 **Discovery**:\n\n{event}\n\nWhat do you do next? (Inspect, take, ignore, etc.)")
            history.append({"role": "assistant", "content": msg.content})
            cl.user_session.set("chat_history", history)
            return

        run_config = RunConfig(model_provider=client) if RunConfig else None
        result = Runner.run_streamed(agent, history, run_config=run_config)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and hasattr(event.data, "delta"):
                await msg.stream_token(event.data.delta)

        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("chat_history", history)

    except Exception as e:
        await msg.stream_token(f"❌ Something went wrong: {str(e)}")