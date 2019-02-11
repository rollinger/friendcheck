import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from facebook.models import Friend

class FriendUpdateForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = ['name', 'avatar',]
        # TODO: Add notes &  add_to_watchlist

class FacebookDatapointForm(forms.Form):
    ownership_check = forms.BooleanField(
        label=_('I confirm that the data is mine and I agree to the Terms and Conditions of this Website.'),
        required=True)
    facebook_source_code = forms.CharField(
        label=_('Paste here the source code of your facebook main page.'),
        widget=forms.Textarea)
