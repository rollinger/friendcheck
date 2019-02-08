import json, re
from itertools import tee#, zip

from django.db import models
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

    timestamps  = models.TextField(_('Sequential Timestamps of Data'),
                null=True, blank=True,)

    _ranks       = models.TextField(_('FB Rank Timeseries'),
                null=True, blank=True, validators=[int_list_validator])

    last_rank   = models.IntegerField(_('Last FB Rank'),null=True, blank=True,)

    created_at  = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('Updated at'), auto_now=True)

    def set_ranks(self, val):
        self._ranks = val

    def get_ranks(self):
        # Deserializes the text to array of int
        return [int(d) for d in self._ranks.split(', ')]

    ranks = property(get_ranks, set_ranks)


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

    datetime    = models.DateTimeField(_('Date Time'), auto_now_add=True)

    fbid_data   = models.TextField(_('FB ID Ranked Data'), validators=[int_list_validator])

    ownership_check = models.BooleanField(_('Ownership of Data confirmed by User'), default=False)

    def __str__(self):
        return "%s: %s" % (self.owner.username, self.datetime)

    def save(self, *args, **kwargs):
        # Save this object and then creates or updates the Friend objects
        super(Datapoint, self).save(*args, **kwargs)
        for rank, fbid in enumerate(self.fbid_data):
            friend, created = Friend.objects.get_or_create(owner=self.owner,fbid=fbid)
            if created:
                friend.timestamps = str(self.datetime)
                friend.ranks = int(rank)
            else:
                friend.timestamps += ', ' + str(self.datetime)
                friend.ranks += ', ' + str(rank)
            friend.last_rank = rank
            # Save Friend Instance
            friend.save()

    class Meta:
        verbose_name = _('Datapoint')
        verbose_name_plural = _('Datapoints')
        ordering = ['datetime']
        unique_together = ("owner","datetime")
