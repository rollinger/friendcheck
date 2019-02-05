from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, RedirectView, UpdateView
from django.views.generic.edit import FormView

from facebook.forms import FacebookDatapointForm
from facebook.models import Datapoint

# Create your views here.
class CreateFBDatapointView(LoginRequiredMixin, FormView):
    template_name = 'facebook/add_datapoint.html'
    form_class = FacebookDatapointForm
    #fields = ["name"]

    def get_success_url(self):
        return reverse("facebook:overview")

    def create_datapoint(self, fbid_data):
        # Creates a Datapoint Object for that User
        datapoint = Datapoint(
            owner = self.request.user,
            fbid_data = fbid_data,
            ownership_check = True
        )
        datapoint.save()

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        fbid_data = form.extract_fbid_data()
        if fbid_data:
            self.create_datapoint(fbid_data)
        return super().form_valid(form)



facebook_add_datapoint_view = CreateFBDatapointView.as_view()
