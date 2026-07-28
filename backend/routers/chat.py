from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.ai_service import get_ai_response
import backend.schemas as schemas
import backend.models as models

router = APIRouter()


# /me must be registered before / and must accept both slash variants.
# A trailing-slash redirect (307) can strip the Authorization header in browsers
# on cross-origin requests, which caused "Could not validate credentials" for
# clients posting to /api/chat/me/ instead of /api/chat/me.


@router.post("/me", response_model=schemas.ChatResponse)
@router.post("/me/", response_model=schemas.ChatResponse, include_in_schema=False)
def chat_with_auth(
    chat_data: schemas.ChatMessage,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Authenticated chat endpoint
    Knows the user's order history too
    """
    reply = get_ai_response(chat_data.message, db, user=current_user)
    return {"reply": reply}


@router.post("/", response_model=schemas.ChatResponse)
def chat(
    chat_data: schemas.ChatMessage,
    db: Session = Depends(get_db),
):
    """
    Public chat endpoint - works without login
    Anyone can ask about products
    """
    reply = get_ai_response(chat_data.message, db, user=None)
    return {"reply": reply}
