from django.contrib.auth import get_user_model, forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms as django_form

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout

User = get_user_model()


class UserChangeForm(forms.UserChangeForm):

    class Meta(forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(forms.UserCreationForm):

    error_message = forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    #invite = django_form.BooleanField(label=_("You confirm you have a valid facebook account."))

    def __init__(self, *args, **kwargs):
        super(forms.UserCreationForm, self).__init__(*args, **kwargs)
        self.order_fields( ['username', 'email', 'invite_code', 'password1', 'password2','has_facebook_account','accept_terms_and_conditions'])
        self.helper = FormHelper()
        self.helper.form_id = 'signup_form'
        self.helper.form_class = 'signup'
        self.helper.form_method = 'post'
        self.helper.form_action = 'account_signup'

        self.helper.add_input(Submit('submit', _('Sign me up!'), css_class="btn btn-primary btn-block"))


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
