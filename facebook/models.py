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

    timestamps  = ArrayField(models.DateTimeField(),null=True, blank=True)

    ranks       = ArrayField(models.IntegerField(),null=True, blank=True)

    last_rank   = models.IntegerField(_('Current Rank'),null=True, blank=True)

    volatility  = ArrayField(models.IntegerField(),null=True, blank=True)

    social_signals = ArrayField(models.IntegerField(),null=True, blank=True)

    created_at  = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('Updated at'), auto_now=True)

    def add_datapoint(self, timestamp, rank):
        # Find index of timestamp
        try:
            idx = self.timestamps.index(timestamp)
        except:
            idx = None

        # Append or update rank at index
        if idx == None:
            if self.timestamps == None:
                # New Array
                self.timestamps = [timestamp]
                self.ranks = [rank]
            else:
                # Append to Array
                self.timestamps.append(timestamp)
                self.ranks.append(rank)
        else:
            # Modify Rank at found index
            self.ranks[idx] = rank
        # calculate volatility and social_signals
        # Save the object
        self.last_rank = self.ranks[-1]
        self.save()

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
        #timestamps = [re.sub(r'\..*', '', d) for d in self.timestamps.split(', ')]
        timestamps = [ t.strftime("%Y-%m-%d %H:%M:%S") for t in self.timestamps]
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
    owner       = models.ForeignKey(User, related_name="datapoints", on_delete=models.CASCADE)

    datetime    = models.DateTimeField(_('Date Time'))

    fbid_data   = models.TextField(_('FB ID List'), null=True, blank=True,
                help_text=_('String of comma-separated list of facebook ids: ["123","456",...]'))

    source_code = models.TextField(_('FB Page Source Code'), null=True, blank=True,
                help_text=_('Source Code of the main facebook page'))

    ownership_check = models.BooleanField(_('Ownership of Data confirmed by User'), default=False)

    integrated  = models.BooleanField(_('Datapoint is integrated in Friends'), default=False)

    created_at  = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('Updated at'), auto_now=True)

    def __str__(self):
        return "%s: %s" % (self.owner.username, self.datetime)

    def integrate_datapoint(self):
        # Extract fbid's from text field
        data = re.findall('\"(\d*)-\d\"', self.fbid_data )
        data = [int( d ) for d in data]
        # Remove duplicates while maintain order
        fbid_list = []
        seen = set()
        seen_add = seen.add
        fbid_list = [x for x in data if not (x in seen or seen_add(x))]
        # Adds each datapoints to Friends or updates it if the timestamp present.
        for rank, fbid in enumerate(fbid_list):
            #print('%s:%d' % (fbid,rank+1) )
            friend, created = Friend.objects.get_or_create(owner=self.owner,fbid=fbid)
            friend.add_datapoint(timestamp=self.datetime,rank=rank+1)

    def save(self, *args, **kwargs):
        super(Datapoint, self).save(*args, **kwargs)
        # call integrate_datapoint (LATER: Asnc, delayed execution)
        # Requirements for Integration:
        #   - fbid_data != Empty or None
        #   - Ownership check == True
        #   - Integrated == False (becomes True after integration)
        if self.fbid_data and self.ownership_check == True and self.integrated == False:
            self.integrate_datapoint()
            self.integrated=True
            super(Datapoint, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Datapoint')
        verbose_name_plural = _('Datapoints')
        ordering = ['datetime']
        unique_together = ("owner","datetime")
