import re
from django.contrib import admin
from django import forms
from .models import Friend, Datapoint

# Register your models here.
class FriendAdmin(admin.ModelAdmin):
     list_display = ["name", "fbid", 'owner','timestamps', 'ranks', 'last_rank',]
     list_display_links = ['fbid']
     #readonly_fields = ["owner", "fbid", 'timestamps', 'ranks',]#
     search_fields = ['name','notes','fbid']
     list_filter = ['owner',]

admin.site.register(Friend, FriendAdmin)



class DatapointAdmin(admin.ModelAdmin):
    list_display = ["owner", "datetime", 'integrated']#
    #readonly_fields = ["integrated",]

admin.site.register(Datapoint, DatapointAdmin)
