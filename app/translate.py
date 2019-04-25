from google.cloud import translate
from google.api_core.exceptions import BadRequest
from app import app


def translate_post(text, to_language):
    if 'TRANSLATE_KEY' not in app.config or not app.config['TRANSLATE_KEY']:
        return 'Error: the translation service is not configured.'
    try:
        client = translate.Client()
        result = client.translate(text, target_language=to_language)
    except BadRequest:
        return 'Error: the translation service failed.'
    if result['translatedText'] == text:
        return 'Error: the translation did not occur.'
    return result['translatedText']