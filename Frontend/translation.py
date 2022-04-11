from modeltranslation.translator import translator, TranslationOptions
from .models import Terms,Privacy
from home.models import News
from Blogs.models import Blog
from taggit.models import Tag
class NewsTranslationOptions(TranslationOptions):
    fields = ['text',]
    required_languages = ["ar"]
translator.register(Terms, NewsTranslationOptions)

class PrivacyTranslate(TranslationOptions):
    fields = ['text',]
    required_languages = ["ar"]
translator.register(Privacy, PrivacyTranslate)


class NewsTranslate(TranslationOptions):
    fields = ['name',]
    required_languages = ["ar"]
translator.register(News, NewsTranslate)

class BlogTranslate(TranslationOptions):
    fields = ['name']
    required_languages = ["ar"]
translator.register(Blog, BlogTranslate)


class TagTranslate(TranslationOptions):
    fields=["name"]
    required_languages=["ar"]
translator.register(Tag, TagTranslate)
