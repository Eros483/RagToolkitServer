# services/translator_service.py
from models.llm_model import llm_model # Assuming your LLM is initialized here
from typing import Dict, Any

model=llm_model

async def translate_text(text: str, target_language: str) -> str:
    """
    Translates the given text into the target language using the LLM.
    """
    # Construct a prompt for the LLM to perform translation
    # It's important to be explicit and clear in the prompt.
    prompt = f"""<|im_start|>system
    You are a highly skilled and accurate language translator.
    Your task is to translate the provided text into {target_language}.
    Do not add any additional commentary, conversational filler, or explanations.
    Only provide the translated text.
    If the text is already in {target_language}, return it as is.
    <|im_end|>
    <|im_start|>user
    Translate the following text into {target_language}:
    "{text}"<|im_end|>
    <|im_start|>assistant
    """
    try:
        # Call the LLM to get the translation
        response = model.create_completion(
            prompt=prompt,
            temperature=0.1, # Keep temperature low for deterministic translation
            max_tokens=len(text) * 2 # Allow enough tokens for translation, roughly double the input length
        )
        
        translated_text = response['choices'][0]['text'].strip()
        return translated_text
    except Exception as e:
        print(f"Error during translation in translator_service: {e}")
        # Fallback to original text or an error message if translation fails
        return f"Translation failed: {e}. Original text: {text}"

