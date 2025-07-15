# routers/translator_router.py
from fastapi import APIRouter, HTTPException, status
from core.models import TranslateRequest, TranslateResponse
from services import translator_service

router = APIRouter(
    prefix="/translator",
    tags=["Translator"]
)

@router.post("/translate_text/", response_model=TranslateResponse, summary="Translate text to a target language")
async def translate_text_endpoint(request: TranslateRequest):
    """
    Translates the provided text to the specified target language using the LLM.
    """
    try:
        translated_text = await translator_service.translate_text(
            text=request.text,
            target_language=request.target_language
        )
        return TranslateResponse(translated_text=translated_text)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Translation failed: {e}")

