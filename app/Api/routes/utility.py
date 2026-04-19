from fastapi import APIRouter

# from app.schemas.utility import BudgetRequest, ChatRequest, ChatResponse, ScanRequest, TranslationRequest  # not yet implemented
# from app.services.ai_router import generate_response  # not yet implemented

router = APIRouter()


@router.post("/chat")
async def chat():
    return {"message": "Not implemented"}


@router.post("/scan")
async def scan():
    return {"message": "Not implemented"}


@router.post("/translate")
def translate():
    return {"message": "Not implemented"}


@router.post("/budget")
def budget():
    return {"message": "Not implemented"}
