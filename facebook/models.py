import json, re, bisect, datetime
from itertools import tee

from django.db import models,transaction
# https://docs.djangoproject.com/en/2.1/ref/contrib/postgres/fields/
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.validators import int_list_validator

from friendcheck.users.models import User

# Facebook stores 400 fbid, after removing for duplicates
MAXRANK = 400

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class Friend(models.Model):
    owner       = models.ForeignKey(User, related_name="friends", on_delete=models.CASCADE)

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

    movement  = ArrayField(models.IntegerField(),null=True, blank=True)

    total_movement   = models.IntegerField(_('Total Rank Movement'),null=True, blank=True)

    social_signals = ArrayField(models.IntegerField(),null=True, blank=True)

    total_social_signals   = models.IntegerField(_('Total Social Signals'),null=True, blank=True)

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
        self.calculate_movement()
        self.calculate_social_signal()
        # Set the last_rank and totals for volatility and social_signals
        self.last_rank = self.ranks[-1]
        # Save the object
        self.save()

    def calculate_movement(self):
        if self.ranks and len(self.ranks) >= 2:
            # Volatility from the last two rank elements
            volatility = (self.ranks[-2]-self.ranks[-1])
            # Create or append to ArrayField
            if self.movement == None:
                self.movement = [volatility]
            else:
                self.movement.append(volatility)
            # Calculate Total Movement
            self.total_movement = 0
            for m in self.movement:
                self.total_movement += m

    def calculate_social_signal(self):
        if self.ranks: #and len(self.ranks) >= 2:
            if len(self.ranks) == 1:
                # Volatility from MAXRANK to the current rank
                a = MAXRANK
                b = self.ranks[-1]
            elif len(self.ranks) >= 2:
                # Social Signals from the last two rank elements
                a = self.ranks[-2]
                b = self.ranks[-1]
            # calculate the estimated delta of social signals based on rank
            if a == b: # maintain rank
                social_signal = (MAXRANK-a)
            elif a < b: # ascending (descending in ranks)
                d = 0
                for r1, r2 in pairwise(range(a,b+1)):
                    d += (MAXRANK-r2)*-1
                social_signal = d
            elif a > b: # descending (ascending in ranks)
                d = 0
                for r1, r2 in pairwise(range(a,b-1,-1)):
                    d += (MAXRANK-r2)
                social_signal = d

            # Create or append to ArrayField
            if self.social_signals == None:
                self.social_signals = [social_signal]
            else:
                self.social_signals.append(social_signal)

            self.total_social_signals = 0
            for ss in self.social_signals:
                self.total_social_signals += ss

    def get_current_movement(self,dp=1):
        # Returns the movement betwen the last dp+1 ranks
        current_movement = None
        last_date = self.owner.timeline_of_datapoints[-1]
        if len(self.timestamps) > 1 and self.timestamps[-1] == last_date:
            current_movement = self.movement[-1]
        return current_movement

    def get_current_social_signals(self,dp=1):
        # Returns the social signals betwen the last dp+1 ranks
        social_signals = None
        last_date = self.owner.timeline_of_datapoints[-1]
        if len(self.timestamps) > 1 and self.timestamps[-1] == last_date:
            social_signals = self.social_signals[-1]
        return social_signals


    def get_rank_timeseries(self):
        # Returns the complete timeseries of rank data for the friend
        timestamps = []
        ranks = []

        for idx, t in enumerate( self.owner.timeline_of_datapoints ):
            timestamps.append( t.strftime("%Y-%m-%d %H:%M:%S") )
            index = None
            # Get the index of the date for rank retrieval
            try:
                if t in self.timestamps:
                    index = self.timestamps.index( self.owner.timeline_of_datapoints[idx] )
            except:
                index = None

            if index != None:
                # Has Data
                ranks.append(self.ranks[index])
            else:
                # Has no data - 'none' suppress point in chartjs
                ranks.append('none')
        return {'timestamps':timestamps, 'ranks':ranks}

    def __str__(self):
        if self.name:
            #return "%s (%s)" % (self.name, self.fbid)
            return "%s" % self.name
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
        #for fbid in data:
        #    if not fbid in fbid_list:
        #        fbid_list.append( fbid )

        # Adds each datapoints to Friends or updates it if the timestamp present.
        for rank, fbid in enumerate(fbid_list):
            #print('%s:%d' % (fbid,rank+1) )
            friend, created = Friend.objects.get_or_create(owner=self.owner,fbid=fbid)
            friend.add_datapoint( timestamp=self.datetime, rank=rank+1 )

    def save(self, *args, **kwargs):
        super(Datapoint, self).save(*args, **kwargs)
        # call integrate_datapoint (LATER: Asnc, delayed execution)
        # Requirements for Integration:
        #   - fbid_data != Empty or None
        #   - Ownership check == True
        #   - Integrated == False (becomes True after integration)
        if self.fbid_data and self.ownership_check == True and self.integrated == False:
            # Integrate the datapoint into friends
            self.integrate_datapoint()
            # Set to integrated and Save
            self.integrated=True
            super(Datapoint, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Datapoint')
        verbose_name_plural = _('Datapoints')
        ordering = ['datetime']
        unique_together = ("owner","datetime")
