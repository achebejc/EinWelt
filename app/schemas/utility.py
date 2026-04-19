from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    language: str = "en"


class ChatResponse(BaseModel):
    response: str
    language: str


class ScanRequest(BaseModel):
    extracted_text: str
    language: str = "en"


class TranslationRequest(BaseModel):
    text: str
    targetLanguage: str


class BudgetRequest(BaseModel):
    income: float
    expenses: float
