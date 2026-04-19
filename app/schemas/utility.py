from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Payload for the AI chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User message to send to the AI assistant",
        examples=["How do I open a bank account in Germany?"],
    )
    language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
        description="BCP-47 language code for the response",
        examples=["en", "de", "fr"],
    )


class ChatResponse(BaseModel):
    """AI assistant reply."""

    response: str = Field(..., description="AI-generated response text")
    language: str = Field(..., description="Language code of the response")


class ScanRequest(BaseModel):
    """Payload for the document scan / OCR analysis endpoint."""

    extracted_text: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        description="Raw text extracted from a scanned document",
    )
    language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
        description="BCP-47 language code for the response",
    )


class TranslationRequest(BaseModel):
    """Payload for the translation endpoint."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Text to translate",
    )
    targetLanguage: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="BCP-47 language code of the target language",
        examples=["de", "fr", "es"],
    )


class BudgetRequest(BaseModel):
    """Payload for the budget analysis endpoint."""

    income: float = Field(..., ge=0, description="Monthly income in the user's currency")
    expenses: float = Field(..., ge=0, description="Total monthly expenses")

