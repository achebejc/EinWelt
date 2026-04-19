from fastapi import APIRouter, Depends

from app.Api.deps import get_current_user
from app.models.user import User
from app.schemas.utility import (
    BudgetRequest,
    ChatRequest,
    ChatResponse,
    ScanRequest,
    TranslationRequest,
)
from app.services.ai_router import generate_response

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, current_user: User = Depends(get_current_user)):
    reply = await generate_response(body.message, body.language, mode="chat")
    return ChatResponse(response=reply, language=body.language)


@router.post("/scan", response_model=ChatResponse)
async def scan(body: ScanRequest, current_user: User = Depends(get_current_user)):
    reply = await generate_response(body.extracted_text, body.language, mode="scan")
    return ChatResponse(response=reply, language=body.language)


@router.post("/translate", response_model=ChatResponse)
async def translate(body: TranslationRequest, current_user: User = Depends(get_current_user)):
    message = f"Translate the following text to {body.targetLanguage}:\n\n{body.text}"
    reply = await generate_response(message, body.targetLanguage, mode="translate")
    return ChatResponse(response=reply, language=body.targetLanguage)


@router.post("/budget", response_model=ChatResponse)
async def budget(body: BudgetRequest, current_user: User = Depends(get_current_user)):
    message = f"Income: {body.income}\nExpenses: {body.expenses}"
    reply = await generate_response(message, "en", mode="budget")
    return ChatResponse(response=reply, language="en")
