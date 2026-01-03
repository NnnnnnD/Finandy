from typing import Dict, Any
from app.bot.states import BotState

BOT_MEMORY: Dict[str, Dict[str, Any]] = {}

def get_state(user_key: str) -> Dict[str, Any]:
    return BOT_MEMORY.get(
        user_key,
        {"state": BotState.IDLE, "pending": None},
    )

def set_state(user_key: str, *, state: BotState, pending=None):
    BOT_MEMORY[user_key] = {
        "state": state,
        "pending": pending,
    }

def clear_state(user_key: str):
    BOT_MEMORY.pop(user_key, None)
