from django.views.generic import TemplateView
# https://github.com/pennersr/django-allauth
from allauth.account.forms import LoginForm, SignupForm

class HomeLandingPage(TemplateView):
    template_name = 'pages/home.html'

    # here we add some context to the already existing context
    def get_context_data(self, **kwargs):
        # we get context data from original view
        context = super(HomeLandingPage, self).get_context_data(**kwargs)
        context['signup_form'] = SignupForm() # add form to context
        context['login_form'] = LoginForm() # add form to context
        # signup==form
        # login==login_form
        return context

home_landing_page = HomeLandingPage.as_view()
