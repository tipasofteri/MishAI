# src/assistant.py

import openai
import google.generativeai as genai
from utils import get_string

def get_completion(prompt: str, provider: str, api_key: str, model: str, language: str, image=None) -> str:
    """
    Отправляет запрос к AI. Может включать изображение.
    """
    if not api_key or "YOUR_API_KEY_HERE" in api_key:
        raise ValueError("API key is not configured.")

    system_message = get_string('system_prompt', language)

    try:
        if provider == 'openai':
            if image:
                return get_string('openai_vision_not_supported', language)
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()

        elif provider == 'gemini':
            genai.configure(api_key=api_key)
            if image and "vision" not in model and "flash" not in model and "pro" not in model:
                 model = 'gemini-1.5-flash'

            gemini_model = genai.GenerativeModel(model)
            
            content = [system_message, prompt]
            if image:
                content.append(image)
            
            response = gemini_model.generate_content(content)
            return response.text.strip()

        else:
            raise ValueError(f"Unknown provider: {provider}.")

    except Exception as e:
        print(f"An error occurred with {provider} API: {e}")
        return get_string('error_api', language).format(provider=provider.capitalize(), error=e)