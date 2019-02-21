from django.contrib.auth import get_user_model, forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms as django_form

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, HTML

from . models import Configuration
User = get_user_model()


class UserChangeForm(forms.UserChangeForm):

    class Meta(forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(forms.UserCreationForm):

    error_message = forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    def __init__(self, *args, **kwargs):
        super(forms.UserCreationForm, self).__init__(*args, **kwargs)
        # Check Signup allowed only with invite Code
        invite_only = Configuration.objects.signup_is_invite_only()
        if invite_only:
            invite_field = Field('invite_code', placeholder=_('Enter your invite code (REQUIRED)'), required="")
        else:
            invite_field = Field('invite_code', placeholder=_('Enter your invite code'))
        self.helper = FormHelper()
        self.helper.form_id = 'signup_form'
        self.helper.form_class = 'signup form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = 'account_signup'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.help_text_inline = False
        self.helper.layout = Layout(
            invite_field,
            HTML('<hr>'),
            Field('username', placeholder=_('Choose your username'), required=""),
            Field('email', placeholder=_('Your email address'), required=""),
            'password1',
            'password2',
            Field('has_facebook_account', required=""),
            Field('accept_terms_and_conditions', required=""),
            Submit('submit', _('Sign me up!'), css_class="btn btn-primary btn-block")
        )

    class Meta(forms.UserCreationForm.Meta):
        model = User
        fields = forms.UserCreationForm.Meta.fields + ('email', 'invite_code','has_facebook_account', \
            'accept_terms_and_conditions')

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])
