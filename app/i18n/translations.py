import json
import os

# Global variable to store current language
current_language = "es"  # Default to Spanish

# Global variable to store translations
translations = {}

def initialize_translations():
    """Initialize translations by loading the default language"""
    load_language(current_language)

def load_language(language_code):
    """Load translations for a specific language"""
    global translations, current_language
    
    try:
        # Construct path to the translation file
        current_dir = os.path.dirname(__file__)
        locale_file = os.path.join(current_dir, 'locales', f'{language_code}.json')
        
        # Load translations from JSON file
        with open(locale_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        current_language = language_code
        print(f"Loaded translations for language: {language_code}")
        
    except FileNotFoundError:
        print(f"Translation file not found for language: {language_code}")
        # Fall back to English if available, otherwise use empty dict
        if language_code != 'en':
            load_language('en')
        else:
            translations = {}
    except Exception as e:
        print(f"Error loading translations: {e}")
        translations = {}

def _(key, default=None):
    """Get translation for a key
    
    Args:
        key: Translation key
        default: Default text if translation not found
    
    Returns:
        Translated text or default or key if not found
    """
    if default is None:
        default = key
    
    return translations.get(key, default)

def set_current_language(language_code):
    """Set the current language and reload translations"""
    load_language(language_code)

def get_current_language():
    """Get the current language code"""
    return current_language

def get_available_languages():
    """Get list of available language codes"""
    try:
        current_dir = os.path.dirname(__file__)
        locales_dir = os.path.join(current_dir, 'locales')
        
        if not os.path.exists(locales_dir):
            return ['en']
        
        languages = []
        for file in os.listdir(locales_dir):
            if file.endswith('.json'):
                lang_code = file[:-5]  # Remove .json extension
                languages.append(lang_code)
        
        return languages if languages else ['en']
    except Exception as e:
        print(f"Error getting available languages: {e}")
        return ['en']