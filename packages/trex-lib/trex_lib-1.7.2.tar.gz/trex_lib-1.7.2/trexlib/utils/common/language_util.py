'''
Created on Dec 16, 2025

@author: jacklok
'''
from flask.globals import request

SUPPORTED_LANGUAGES = ['en', 'ms', 'zh']
DEFAULT_LANGUAGE    = 'en'

def get_preferred_language():
    # returns best match based on Accept-Language
    lang = request.accept_languages.best_match(SUPPORTED_LANGUAGES)
    return lang or DEFAULT_LANGUAGE
