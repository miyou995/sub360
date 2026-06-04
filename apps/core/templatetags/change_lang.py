from django import template
from django.urls import translate_url
from django.templatetags.static import static


register = template.Library()


@register.simple_tag()
def change_lang(path, lang):
    return translate_url(path, lang)


@register.simple_tag
def get_lang_icon(lang):
    return static(f"images/flags/{lang}.svg")
