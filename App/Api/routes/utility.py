from fastapi import APIRouter
from App.schemas.utility import BudgetRequest, ChatRequest, ChatResponse, ScanRequest, TranslationRequest
from App.services.ai_router import generate_response

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    result = await generate_response(message=payload.message, language=payload.language)
    return result

@router.post("/scan", response_model=ChatResponse)
async def scan(payload: ScanRequest):
    message = (
        "Analyze this scanned text for a regular person. "
        "Give: 1) what it is, 2) the important details, 3) what to do next.\n\n"
        f"Scanned text:\n{payload.extracted_text}"
    )
    result = await generate_response(message=message, mode="scan", language=payload.language)
    return result

@router.post("/translate")
def translate(payload: TranslationRequest):
    text = payload.text.strip()
    target = payload.targetLanguage
    return {
        "translatedText": f"[{target}] {text}",
        "mode": "fallback",
        "note": "Wire a dedicated translation provider or model for production quality."
    }

@router.post("/budget")
def budget(payload: BudgetRequest):
    income = float(payload.income)
    expenses = float(payload.expenses)
    remaining = income - expenses
    savings_rate = 0 if income <= 0 else round(max(remaining, 0) / income, 2)
    return {
        "income": income,
        "expenses": expenses,
        "remaining": remaining,
        "savings_rate": savings_rate,
        "status": "positive" if remaining >= 0 else "negative",
        "tips": [
            "Track recurring costs first.",
            "Protect essentials before optional spending.",
            "Set one short savings target for the next 30 days.",
        ],
    }
