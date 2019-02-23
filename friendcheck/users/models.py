from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, DateTimeField, BooleanField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils import timezone
import datetime

from . paypal_conf import PAYPAL_RECEIVER_EMAIL, SUBSCRIPTION_PLANS_DETAILS

FREE_DATAPOINTS = 5
TIME_BETWEEN_ADD_DATAPOINTS = 24*60*60

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

    has_facebook_account = models.BooleanField(_('I confirm that I have a valid facebook account.'), default=False)
    accept_terms_and_conditions = models.BooleanField(_('I agree to the Terms and Conditions and Privacy Policy of this website.'), default=False)

    invite_code = CharField(_("Invite Code for Signup"), blank=True, max_length=55)

    subscription_type = CharField(_('Type of Subscription'), max_length=255, choices=SUBSCRIPTION_TYPES, default='0')
    subscription_valid_until = DateTimeField(_("Subscription valid until"), blank=True, null=True )

    timeline_of_datapoints  = ArrayField(DateTimeField(), null=True, blank=True)

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

    def add_timestamp_to_timeline(self, timestamp):
        # Adds the timestamp to the continuous timeline of datapoints
        #if len(self.timeline_of_datapoints) < 1:
        #    self.timeline_of_datapoints = []
            #self.save()
            #self.refresh_from_db()
            #print('NEW')
            #print(self.timeline_of_datapoints)
        self.timeline_of_datapoints.extend( [timestamp] )
        self.save()

        #self.save(update_fields=('timeline_of_datapoints',))
        #print('APPEND')
        #print(self.timeline_of_datapoints)

        #print(self.timeline_of_datapoints)

    def time_since_last_datapoint_added(self):
        # Returns seconds since last add_datapoint
        #abs((d2 - d1).days)
        td = abs( timezone.now() - self.timeline_of_datapoints[-1])
        return td.total_seconds()

    def time_freeze_add_datapoint_reached(self):
        # Check if last datapoint is older than 24 hours
        try:
            if self.time_since_last_datapoint_added() <= TIME_BETWEEN_ADD_DATAPOINTS:
                return False
        except: # not found
            pass
        return True

    def time_next_datapoint_can_be_added(self):
        seconds = TIME_BETWEEN_ADD_DATAPOINTS - self.time_since_last_datapoint_added()
        return str( datetime.timedelta(seconds=seconds) ).split('.')[0]

    def perm_add_datapoint(self):
        # Checks if the User:
        #   - is not authenticated
        #   - has FREE_DATAPOINTS (3) already used
        #   - the subscription_valid_until date is in the past
        #   - has added a datapoint in the last 24 hours
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
    def signup_is_invite_only(self):
        try:
            if self.get(key='SIGNUP_INVITE_ONLY').value == "True":
                return True
            else:
                return False
        except:
            return False

    def signup_is_allowed(self):
        try:
            if self.get(key='SIGNUP_ALLOWED').value == "True":
                return True
            else:
                return False
        except:
            return False

    def signup_max_user_reached(self):
        try:
            if User.objects.filter(is_active=True).count() >= int( self.get(key='SIGNUP_MAX_USERS').value ):
                return True
            else:
                return False
        except:
            return False

    def signup_is_open(self):
        if self.signup_is_allowed() == True and self.signup_max_user_reached() == False:
            return True
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
