from modeltranslation.translator import translator, TranslationOptions
from .models import Terms,Privacy

class NewsTranslationOptions(TranslationOptions):
    fields = ['text',]
    required_languages = ["ar"]
translator.register(Terms, NewsTranslationOptions)

class PrivacyTranslate(TranslationOptions):
    fields = ['text',]
    required_languages = ["ar"]
translator.register(Privacy, PrivacyTranslate)