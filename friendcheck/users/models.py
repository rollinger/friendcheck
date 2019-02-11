from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, DateTimeField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils import timezone

FREE_DATAPOINTS = 3

SUBSCRIPTION_TYPES = (
    ('0', 'FREE'),  # no costs; up to FREE_DATAPOINTS allowed
    ('1', 'BUDDY'), # USD 5.99; add datapoints for 30 days
    ('2', 'VIP'),   # no costs; add datapoints unlimited
)

SUBSCRIPTION_PLANS = ()

class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)

    subscription_type = CharField(_('Type of Subscription'), max_length=255,choices=SUBSCRIPTION_TYPES, default='0')
    subscription_valid_until = DateTimeField(_("Subscription valid until"), blank=True, null=True )

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
        return HttpResponseRedirect("/subscribe/")
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
        return HttpResponseRedirect("/subscribe/")
    return wrapper


#class Booking(models.Model):
#    owner       = models.ForeignKey(User, on_delete=models.CASCADE)
#    created_at  = models.DateTimeField(_('Created at'), auto_now_add=True)
#    updated_at  = models.DateTimeField(_('Updated at'), auto_now=True)
