from fastapi import HTTPException, status
from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings

_SYSTEM_PROMPTS: dict[str, str] = {
    "chat": (
        "You are EinWelt, a helpful multilingual financial assistant. "
        "Answer clearly and concisely in the language requested by the user."
    ),
    "scan": (
        "You are EinWelt, a financial document analyser. "
        "Extract key financial figures and summarise the document in the language requested."
    ),
    "translate": (
        "You are a professional translator. "
        "Translate the provided text accurately into the target language."
    ),
    "budget": (
        "You are EinWelt, a personal finance advisor. "
        "Analyse the income and expenses provided and give actionable budgeting advice."
    ),
}


async def generate_response(message: str, language: str = "en", mode: str = "chat") -> str:
    """
    Send *message* to the OpenAI Chat Completions API and return the assistant
    reply as a plain string.

    Raises HTTP 503 when the OpenAI API key is not configured, and HTTP 502
    when the upstream API call fails.
    """
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are not configured on this server.",
        )

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    system_prompt = _SYSTEM_PROMPTS.get(mode, _SYSTEM_PROMPTS["chat"])
    user_content = f"[Language: {language}]\n\n{message}"

    try:
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.7,
            max_tokens=1024,
        )
    except OpenAIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenAI error: {exc}",
        ) from exc

    return completion.choices[0].message.content or ""
