from google.cloud import translate
from google.api_core.exceptions import BadRequest
from flask import current_app


def translate_post(text, to_language):
    if 'TRANSLATE_KEY' not in current_app.config or not current_app.config['TRANSLATE_KEY']:
        return 'Error: the translation service is not configured.'
    try:
        client = translate.Client()
        result = client.translate(text, target_language=to_language)
    except BadRequest:
        return 'Error: the translation service failed.'
    if result['translatedText'] == text:
        return 'Error: the languages are the same.'
    return result['translatedText']