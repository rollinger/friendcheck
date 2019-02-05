from django.contrib import admin

from .models import Friend, Datapoint

# Register your models here.
class FriendAdmin(admin.ModelAdmin):
     pass

admin.site.register(Friend, FriendAdmin)

class DatapointAdmin(admin.ModelAdmin):
     pass

admin.site.register(Datapoint, DatapointAdmin)
