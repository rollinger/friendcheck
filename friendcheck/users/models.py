from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, DateTimeField, BooleanField
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils import timezone
import datetime

from . paypal_conf import PAYPAL_RECEIVER_EMAIL, SUBSCRIPTION_PLANS_DETAILS

FREE_DATAPOINTS = 5

SUBSCRIPTION_TYPES = (
    ('0', 'FREE'),  # no costs; up to FREE_DATAPOINTS allowed
    ('1', 'BUDDY'), # USD 5.99; add datapoints for 30 days
    ('2', 'VIP'),   # no costs; add datapoints unlimited
)

SUBSCRIPTION_PLANS = (
    ('0', 'MONTHLY'),           # USD 5.99;
    ('1', 'MONTHLY DISCOUNT'),  # USD 3.99;
    ('2', 'YEARLY'),            # USD 45.0;
)



class User(AbstractUser):

    # First Name and Last Name do not cover name patterns around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)

    has_facebook_account = models.BooleanField(_('Confirm that you have a valid facebook account'), default=False)
    accept_terms_and_conditions = models.BooleanField(_('Confirm to subscribe to the Terms and Conditions'), default=False)

    invite_code = CharField(_("Invite Code for Signup"), blank=True, max_length=55)

    subscription_type = CharField(_('Type of Subscription'), max_length=255, choices=SUBSCRIPTION_TYPES, default='0')
    subscription_valid_until = DateTimeField(_("Subscription valid until"), blank=True, null=True )

    def extend_subscription(self, days_increment):
        # Days to be extended
        #days_increment = SUBSCRIPTION_PLANS_DETAILS[subscription_plan]['subscription_extention_days']
        if self.subscription_valid_until == None:
            # Create Subscription (no subscription before)
            self.subscription_valid_until = timezone.now() + datetime.timedelta(days=days_increment)
            # Set subscription_type to 'BUDDY'
            self.subscription_type = '1'
        elif timezone.now() > self.subscription_valid_until:
            # Renew Subscription (subscription in the past)
            self.subscription_valid_until = timezone.now() + datetime.timedelta(days=days_increment)
        elif timezone.now() < self.subscription_valid_until:
            # Extend Subscription (Current Subscription still valid)
            self.subscription_valid_until += datetime.timedelta(days=days_increment)
        # Save User Object
        self.save()

    def datapoints_left(self):
        # Returns the total of datapoints left
        val = FREE_DATAPOINTS - self.datapoints.count()
        return val

    def perm_add_datapoint(self):
        # Checks if the User:
        #   - is not authenticated
        #   - has FREE_DATAPOINTS (3) already used
        #   - the subscription_valid_until date is in the past
        # Returns False if any of the above are True
        # Gives Permission otherwise.
        if not self.is_authenticated:
            print('Not Authenticated')
            return False
        if self.subscription_valid_until:
            if timezone.now() > self.subscription_valid_until:
                print('Subscription expired or None')
                return False
        elif self.datapoints.all().count() >= FREE_DATAPOINTS:
            print('Free Datapoints exceeded')
            return False
        # Otherwise Give Permission
        return True

    def perm_update_friend(self):
        # Checks if the User:
        #   - is not authenticated
        #   - the subscription_valid_until date is in the past
        # Returns False if any of the above are True
        # Gives Permission otherwise.
        if not self.is_authenticated:
            print('Not Authenticated')
            return False
        if self.subscription_valid_until:
            if timezone.now() > self.subscription_valid_until:
                print('Subscription expired or None')
                return False
        return True

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


def can_add_datapoint_permission(function):
    def wrapper(obj, request, *args, **kw):
        # Login Required Test
        decorated_view_func = login_required(request)
        if not decorated_view_func.user.is_authenticated:
            return decorated_view_func(request)  # restricts without login and sends to signin view
        # Permission Test: Can add a datapoint
        if request.user.perm_add_datapoint():# and request.user.is_active:
               return function(obj, request, *args, **kw)
        return HttpResponseRedirect(request.user.get_absolute_url())
    return wrapper

def can_update_friend_permission(function):
    def wrapper(obj, request, *args, **kw):
        # Login Required Test
        decorated_view_func = login_required(request)
        if not decorated_view_func.user.is_authenticated:
            return decorated_view_func(request)  # restricts without login and sends to signin view
        # Permission Test: Can add a datapoint
        if request.user.perm_update_friend():# and request.user.is_active:
               return function(obj, request, *args, **kw)
        return HttpResponseRedirect(request.user.get_absolute_url())
    return wrapper


class Booking(Model):
    owner       = models.ForeignKey(User, related_name="bookings", on_delete=models.CASCADE)

    #ipn_obj     = models.ForeignKey(User, related_name="bookings", on_delete=models.CASCADE)

    subscription_plan = CharField(_('Subscription Deal'), max_length=255, choices=SUBSCRIPTION_PLANS, default='0')
    payment_complete  = BooleanField(_('Payment Completed'), default=False)
    payment_completion_date  = DateTimeField(_('Payment Completion Date'), blank=True, null=True)

    created_at  = DateTimeField(_('Created at'), auto_now_add=True)
    updated_at  = DateTimeField(_('Updated at'), auto_now=True)

    def complete_subscription(self):
        if not self.payment_complete:
            self.payment_complete = True
            self.payment_completion_date = timezone.now()
            self.save()
            # Extend subscription on the User Object
            self.owner.extend_subscription(self.subscription_plan)


class ConfigurationManager(models.Manager):
    # def signup_is_allowed()
    # def signup_max_user_reached()
    def signup_is_invite_only(self):
        try:
            if self.get(key='SIGNUP_INVITE_ONLY').value == "True":
                return True
            else:
                return False
        except:
            return False


class Configuration(models.Model):
    # Configuration Storage for Site Wide Settings
    # SIGNUP ALLOWED        :: Enables, disables Signup
    # SIGNUP INVITE ONLY    :: Restricts Signup to invite codes
    # SIGNUP_MAX_USERS      :: Restricts Signup by a number of users
    # INVITE CODES          :: List of Invite Codes 6chars long
    key     = models.CharField(_('Key'), max_length=255, unique=True)
    value   = models.TextField(_('Value'), null=True, blank=True)

    created_at  = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('Updated at'), auto_now=True)

    objects = ConfigurationManager()

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = _('Configuration')
        verbose_name_plural = _('Configurations')
        ordering = ['-key']
