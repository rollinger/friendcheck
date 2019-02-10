import json, re
from itertools import tee

from django.db import models
# https://docs.djangoproject.com/en/2.1/ref/contrib/postgres/fields/
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.validators import int_list_validator

from friendcheck.users.models import User

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class Friend(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.CASCADE)

    fbid        = models.CharField(_('Facebook ID'), max_length=255)

    name        = models.CharField(_('Friend Name'),
                null=True, blank=True, max_length=255)

    notes       = models.TextField(_('Notes'), null=True, blank=True,
                max_length=2000)

    avatar      = models.ImageField(_('Friend Avatar'),
                upload_to='Friends/', null=True, blank=True)

    timestamps  = ArrayField(models.DateTimeField(),default=[])

    ranks       = ArrayField(models.IntegerField(),default=[])

    volatility  = ArrayField(models.IntegerField(),default=[])

    social_signals = ArrayField(models.IntegerField(),default=[])

    created_at  = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('Updated at'), auto_now=True)


    def absolute_volatility(self):
        volatility = 0
        for a, b in pairwise(self.ranks):
            volatility += abs(a-b)
        return volatility

    def volatility(self):
        volatility = 0
        for a, b in pairwise(self.ranks):
            volatility += (a-b)
        return volatility

    def get_rank_timeseries(self):
        # Returns the timeseries of rank data for the friend
        timestamps = [re.sub(r'\..*', '', d) for d in self.timestamps.split(', ')]
        timeseries = {'timestamps':timestamps, 'ranks':self.ranks}
        return timeseries

    def __str__(self):
        if self.name:
            return "%s (%s)" % (self.name, self.fbid)
        else:
            return "%s" % self.fbid

    def get_facebook_id_url(self):
        # returns the url of the profile on facebook
        return 'https://www.facebook.com/'+str(self.fbid)

    def get_absolute_url(self):
        return reverse("facebook:friend-detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = _('Friend')
        verbose_name_plural = _('Friends')
        ordering = ['-fbid']
        unique_together = ("owner","fbid")


class Datapoint(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.CASCADE)

    datetime    = models.DateTimeField(_('Date Time'))

    # https://docs.djangoproject.com/en/2.1/ref/contrib/postgres/fields/
    fbid_data   = ArrayField(models.IntegerField(),default=[])

    ownership_check = models.BooleanField(_('Ownership of Data confirmed by User'), default=False)

    integrated  = models.BooleanField(_('Datapoint is integrated in Friends'), default=False)

    def __str__(self):
        return "%s: %s" % (self.owner.username, self.datetime)

    def integrate_datapoint(self):
        # Adds the datapoints to Friends or updates it if the timestamp present.
        pass

    def save(self, *args, **kwargs):
        # Save this object and then creates or updates the Friend objects
        super(Datapoint, self).save(*args, **kwargs)
        #for rank, fbid in enumerate(self.fbid_data):
        #    friend, created = Friend.objects.get_or_create(owner=self.owner,fbid=fbid)
        #    if created:
        #        friend.timestamps = str(self.datetime)
        #        friend.ranks = int(rank)
        #    else:
        #        friend.timestamps += ', ' + str(self.datetime)
        #        friend.ranks += ', ' + str(rank)
        #    friend.last_rank = rank
        #    # Save Friend Instance
        #    friend.save()

    class Meta:
        verbose_name = _('Datapoint')
        verbose_name_plural = _('Datapoints')
        ordering = ['datetime']
        unique_together = ("owner","datetime")
