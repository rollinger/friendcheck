import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from facebook.models import Friend

class FriendUpdateForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = ['name', 'comparison', 'avatar', 'color']
        # TODO: Add notes & Tags

class FacebookDatapointForm(forms.Form):
    facebook_source_code = forms.CharField(
        label=_('Paste here the whole source code of your logged in facebook main page.'),
        widget=forms.Textarea)
    ownership_check = forms.BooleanField(
        label=_('I agree to the <a href="/terms_and_conditions/" target="_blank">Terms and Conditions</a> and <a href="/privacy_policy/" target="_blank">Privacy Policy</a> of this website and I want to upload my data for private, educational purposes.'),
        required=True)
