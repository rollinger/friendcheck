from django.views.generic import TemplateView
from django.views.generic.edit import FormView
# https://github.com/pennersr/django-allauth
from allauth.account.forms import LoginForm
from friendcheck.users.forms import UserCreationForm
from friendcheck.users.models import Configuration

class HomeLandingPage(TemplateView):
    template_name = 'pages/home.html'

    # here we add some context to the already existing context
    def get_context_data(self, **kwargs):
        # we get context data from original view
        context = super(HomeLandingPage, self).get_context_data(**kwargs)
        context['signup_is_open'] = Configuration.objects.signup_is_open()
        context['signup_form'] = UserCreationForm() # add form to context
        context['login_form'] = LoginForm() # add form to context
        return context

home_landing_page = HomeLandingPage.as_view()



class TermsAndConditionsView(TemplateView):
    template_name = 'pages/terms_and_conditions.html'
terms_and_conditions = TermsAndConditionsView.as_view()

class PrivacyPolicyView(TemplateView):
    template_name = 'pages/privacy_policy.html'
privacy_policy = PrivacyPolicyView.as_view()
