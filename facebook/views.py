import re
from django.utils import timezone

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView #CreateView, DetailView, , RedirectView, UpdateView
from django.views.generic.edit import FormView

from facebook.forms import FacebookDatapointForm, FriendUpdateForm
from facebook.models import Datapoint, Friend

from friendcheck.users.models import can_add_datapoint_permission, can_update_friend_permission

# Displays the data about one friend
class FriendDetailView(LoginRequiredMixin, UpdateView):
    model = Friend
    form_class = FriendUpdateForm
    template_name = 'facebook/friend-detail.html'

facebook_friend_view = FriendDetailView.as_view()

# Overview View
class FBOverviewView(LoginRequiredMixin, ListView):
    template_name = 'facebook/start.html'
    context_object_name = 'friend_list'

    def get_queryset(self):
        object_list = Friend.objects.filter(owner=self.request.user).order_by('last_rank')
        return object_list

facebook_overview_view = FBOverviewView.as_view()

# Create FB Datapoint
class CreateFBDatapointView(FormView):
    template_name = 'facebook/add_datapoint.html'
    form_class = FacebookDatapointForm

    @can_add_datapoint_permission
    def dispatch(self, *args, **kwargs):
         return super(CreateFBDatapointView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse("facebook:overview")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        fbid_data = self.extract_fbid_data(form.cleaned_data['facebook_source_code'])
        # Create Datapoint
        datapoint = Datapoint(
            owner = self.request.user,
            fbid_data = fbid_data,
            datetime = timezone.now(),
            source_code = form.cleaned_data['facebook_source_code'],
            ownership_check = form.cleaned_data['ownership_check']
        )
        datapoint.save()
        return super().form_valid(form)

    def extract_fbid_data(self, source_code):
        # Returns the list of facebook ids as a json list (python string)

        # Get the relevant data stream between the start and end marker
        data_stream = ""
        start_marker = r"InitialChatFriendsList(.+?)list:"
        end_marker = r",shortProfiles"
        compiled_regex = start_marker + '(.+?)' + end_marker
        try:
            data_stream = re.search(compiled_regex, source_code).group(2)
        except AttributeError:
            # data stream not found in the original facebook_source_code
            # TODO: apply your error handling
            data_stream = ''
        # Returns the json list
        return data_stream

facebook_add_datapoint_view = CreateFBDatapointView.as_view()
