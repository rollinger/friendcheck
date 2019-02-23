from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpRequest

from . models import Configuration

class AccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request: HttpRequest):
        open = False
        if getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True):
            open = Configuration.objects.signup_is_allowed()
        return open


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        # Disallow social login
        return False #getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
