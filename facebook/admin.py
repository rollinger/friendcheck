from django.contrib import admin

from .models import Friend, Datapoint

# Register your models here.
class FriendAdmin(admin.ModelAdmin):
     list_display = ["name", "fbid", 'owner','timestamps', 'ranks', 'last_rank']
     list_display_links = ['fbid']
     readonly_fields = ["owner", "fbid", 'timestamps', 'ranks','last_rank']#
     search_fields = ['name','notes','fbid']
     list_filter = ['owner',]

admin.site.register(Friend, FriendAdmin)

class DatapointAdmin(admin.ModelAdmin):
     list_display = ["owner", "datetime"]
     #readonly_fields = ["owner", "datetime", 'ownership_check', 'fbid_data']#

admin.site.register(Datapoint, DatapointAdmin)
