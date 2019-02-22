import re
from django.contrib import admin
from django import forms
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Friend, Datapoint


class FriendResource(resources.ModelResource):

    class Meta:
        model = Friend
        import_id_fields = ('fbid',)
        fields = ('fbid', 'name',)

# Register your models here.
class FriendAdmin(ImportExportModelAdmin):
     list_display = ["name", "fbid", 'owner', 'ranks', 'total_social_signals', \
        'total_movement', 'last_rank',]
     list_display_links = ['fbid']
     #readonly_fields = ["owner", "fbid", 'timestamps', 'ranks',]#
     search_fields = ['name','notes','fbid']
     list_filter = ['owner',]

     resource_class = FriendResource

     actions = ['delete_timeserie_data']

     def delete_timeserie_data(self, request, queryset):
         for friend in queryset:
             friend.timestamps = None
             friend.ranks = None
             friend.last_rank = None
             friend.movement = None
             friend.total_movement = None
             friend.social_signals = None
             friend.total_social_signals = None
             friend.save()
     delete_timeserie_data.short_description = "Clear the timeserie of selected Friends"

admin.site.register(Friend, FriendAdmin)



class DatapointAdmin(admin.ModelAdmin):
    list_display = ["owner", "datetime", 'ownership_check', 'integrated']
    list_display_links = ['datetime']
    #readonly_fields = ["integrated",]
    list_filter = ['ownership_check', 'integrated', 'owner',]

    actions = ['reintegrate_datapoints']

    def reintegrate_datapoints(self, request, queryset):
        # Add timeline
        timeline = []
        #self.owner.add_timestamp_to_timeline(self.datetime)
        # Integrate Datapoint (disable the continuous timeline)
        for datapoint in queryset:
            timeline.append(datapoint.datetime)
            datapoint.integrated = False
            datapoint.save()

        d = queryset.first()
        d.owner.timeline_of_datapoints.extend(timeline)
        d.owner.save()
    reintegrate_datapoints.short_description = "Reintegrate selected Datapoints"

admin.site.register(Datapoint, DatapointAdmin)
