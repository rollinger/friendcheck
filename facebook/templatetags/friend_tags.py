from django import template
from facebook.models import Friend

register = template.Library()


@register.simple_tag
def get_statistics(friend, last_date):
    return friend.get_statistics(last_date)

@register.filter
def index(List, i):
    return List[int(i)]
