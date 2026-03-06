from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.chat_service import get_chat_response

router = APIRouter(prefix="/chat", tags=["Chat Assistant"])


@router.post("/", response_model=ChatResponse)
def chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Send a message to the AI chat assistant."""
    result = get_chat_response(db, chat_request.session_id, chat_request.message)
    return result
