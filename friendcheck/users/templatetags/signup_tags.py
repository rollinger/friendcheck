# DOC: https://docs.djangoproject.com/en/1.10/howto/custom-template-tags/
from django import template
from friendcheck.users.models import Configuration

register = template.Library()


@register.simple_tag
def signup_is_open():
    return Configuration.objects.signup_is_open()
