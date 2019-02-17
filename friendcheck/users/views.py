from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from . models import PAYPAL_RECEIVER_EMAIL, SUBSCRIPTION_PLANS_DETAILS

User = get_user_model()

def generate_unique_invoice_id(user_object):
    # Generates a unique invoice id in the format
    # FC-<user-pk>-<current_date>-<user-username>
    unique_user_id = "FC-{}-{}-{}".format( str(user_object.pk), \
        str(timezone.now().strftime("%Y%m%d%H%M%S")), \
        str(user_object.username))
    return unique_user_id


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

user_detail_view = UserDetailView.as_view()


class UserListView(LoginRequiredMixin, ListView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_list_view = UserListView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class UserSubscriptionView(LoginRequiredMixin, TemplateView):
    #https://django-paypal.readthedocs.io/en/stable/standard/ipn.html
    template_name = "users/user_subscription.html"

    def get_context_data(self, **kwargs):
        context = super(UserSubscriptionView, self).get_context_data(**kwargs)

        paypal_dict_30_days = {
            "business": PAYPAL_RECEIVER_EMAIL,
            "amount": SUBSCRIPTION_PLANS_DETAILS['MONTHLY']['price_usd'],
            "item_name": SUBSCRIPTION_PLANS_DETAILS['MONTHLY']['item_name'],
            "invoice": generate_unique_invoice_id(self.request.user),
            "notify_url": self.request.build_absolute_uri(reverse('paypal-ipn')),
            "return": self.request.build_absolute_uri(reverse('users:subscription-success')),
            "cancel_return": self.request.build_absolute_uri(reverse('users:subscription-canceled')),
            "custom": "monthly_plan",  # Custom command to correlate to some function later (optional)
        }
        context['paypal30daysform'] = PayPalPaymentsForm(initial=paypal_dict_30_days)
        #context['paypal365daysform'] = PayPalPaymentsForm(initial=paypal_dict_365_days)

        # Process messages if the view is called by cancel return or success-return
        if self.request.path == reverse('users:subscription-canceled'):
            messages.add_message(self.request, messages.ERROR,
                _('Your payment attempt for your subscription was canceled!'), fail_silently=True)
        elif self.request.path == reverse('users:subscription-success'):
            messages.add_message(self.request, messages.SUCCESS,
                _('Your payment for your subscription was successfully completed! Your Subscription Date will update shortly.'), fail_silently=True)
        # Return the Context
        return context

user_subscription_view = UserSubscriptionView.as_view()
