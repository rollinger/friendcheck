import re

from django import forms
from django.utils.translation import ugettext_lazy as _



class FacebookDatapointForm(forms.Form):
    ownership_check = forms.BooleanField(
        label=_('I confirm that the data is mine and I agree to the Terms and Conditions of this Website.'),
        required=True)
    facebook_source_code = forms.CharField(
        label=_('Paste here the source code of your facebook page.'),
        widget=forms.Textarea)

    def extract_fbid_data(self):
        # takes valid form data extracts the data and
        # returns the list of facebook ids

        # Get the relevant data stream between the start and end marker
        data_stream = ""
        start_marker = r"InitialChatFriendsList(.+?)list:\["
        end_marker = r"\],shortProfiles"
        compiled_regex = start_marker + '(.+?)' + end_marker
        try:
            data_stream = re.search(compiled_regex, self.cleaned_data['facebook_source_code']).group(2)
        except AttributeError:
            # data stream not found in the original facebook_source_code
            # TODO: apply your error handling
            data_stream = ''

        # Extract the list of fbid from the data stream and clean up a bit
        fbid_list = []
        if data_stream:
            data = data_stream.split('\",\"')
            data = [re.sub(r'-\d', '', d) for d in data]
            data = [int( re.sub(r'\"', '', d) ) for d in data]
            fbid_list = data

        return fbid_list
