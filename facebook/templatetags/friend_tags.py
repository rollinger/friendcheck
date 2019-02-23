# DOC: https://docs.djangoproject.com/en/1.10/howto/custom-template-tags/
from django import template
from facebook.models import Friend

register = template.Library()


@register.simple_tag
def get_statistics(friend, last_date):
    return friend.get_statistics(last_date)

@register.filter
def index(List, i):
    if List:
        return List[int(i)]
    return None
