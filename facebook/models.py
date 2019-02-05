from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.validators import int_list_validator

from friendcheck.users.models import User



class Friend(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.CASCADE)

    fbid        = models.CharField(_('Facebook ID'), max_length=255)

    notes       = models.TextField(_('Notes'), null=True, blank=True,
                max_length=2000)

    avatar      = models.ImageField(_('Friend Avatar'),
                upload_to='Friends/', null=True, blank=True)

    #timestamp_array   = models.TextField(_('FB ID Ranked Data'), validators=[int_list_validator])
    #rank_array   = models.TextField(_('FB ID Ranked Data'), validators=[int_list_validator])

    created_at  = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('Updated at'), auto_now=True)

    #def get_absolute_url(self):
    #    return reverse("users:detail", kwargs={"username": self.username})



class Datapoint(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.CASCADE)

    datetime    = models.DateTimeField(_('Date Time'), auto_now_add=True)

    fbid_data   = models.TextField(_('FB ID Ranked Data'), validators=[int_list_validator])
