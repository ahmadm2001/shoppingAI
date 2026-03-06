import json
from sqlalchemy.orm import Session
from openai import OpenAI

from app.config.settings import get_settings
from app.config.redis import get_redis
from app.models.item import Item

settings = get_settings()

CHAT_COUNT_PREFIX = "chat_count:"
CHAT_HISTORY_PREFIX = "chat_history:"
CHAT_COUNT_TTL = 3600  # 1 hour session


def get_chat_response(db: Session, session_id: str, user_message: str) -> dict:
    """Process a chat message and return AI response with remaining prompts."""
    redis = get_redis()
    count_key = f"{CHAT_COUNT_PREFIX}{session_id}"
    history_key = f"{CHAT_HISTORY_PREFIX}{session_id}"

    # Check prompt count
    current_count = redis.get(count_key)
    current_count = int(current_count) if current_count else 0

    if current_count >= settings.CHAT_PROMPT_LIMIT:
        return {
            "reply": "You have reached the maximum number of prompts for this session (5/5). Please start a new session.",
            "prompts_remaining": 0,
        }

    # Get all items for context
    items = db.query(Item).all()
    items_context = _build_items_context(items)

    # Get conversation history
    history_raw = redis.get(history_key)
    history = json.loads(history_raw) if history_raw else []

    # Build messages
    system_message = (
        "You are a helpful shopping assistant for our online store. "
        "You help customers with questions about products available in our store. "
        "Here are the current products in our store:\n\n"
        f"{items_context}\n\n"
        "Answer questions about these products, including availability, pricing, "
        "descriptions, and general product information. "
        "If a product is out of stock (stock = 0), let the customer know. "
        "Be friendly and helpful. If asked about products we don't carry, "
        "let the customer know we don't have that item."
    )

    messages = [{"role": "system", "content": system_message}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # Call OpenAI API
    try:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url="https://api.openai.com/v1",
         )
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"I'm sorry, I'm having trouble connecting right now. Please try again later. Error: {str(e)}"

    # Update history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    redis.setex(history_key, CHAT_COUNT_TTL, json.dumps(history))

    # Increment count
    new_count = current_count + 1
    redis.setex(count_key, CHAT_COUNT_TTL, str(new_count))

    return {
        "reply": reply,
        "prompts_remaining": settings.CHAT_PROMPT_LIMIT - new_count,
    }


def _build_items_context(items: list[Item]) -> str:
    """Build a text description of all items for the AI context."""
    lines = []
    for item in items:
        stock_status = f"{item.stock} in stock" if item.stock > 0 else "OUT OF STOCK"
        lines.append(
            f"- {item.name} | ${item.price:.2f} | {stock_status} | "
            f"Category: {item.category or 'N/A'} | "
            f"Description: {item.description or 'N/A'}"
        )
    return "\n".join(lines) if lines else "No products available."
