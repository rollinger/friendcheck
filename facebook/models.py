from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class Friend(models.Model):
    pass
    # First Name and Last Name do not cover name patterns
    # around the globe.
    #name = CharField(_("Name of User"), blank=True, max_length=255)

    #def get_absolute_url(self):
    #    return reverse("users:detail", kwargs={"username": self.username})

class Datapoint(models.Model):
    pass
