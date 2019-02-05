from django.urls import path
from django.views.generic import TemplateView

#from facebook.views import (
#   facebook_add_datapoint_view
#    user_list_view,
#    user_redirect_view,
#    user_update_view,
#    user_detail_view,
#)

app_name = "facebook"
urlpatterns = [
    path("", TemplateView.as_view(template_name="facebook/start.html"), name="overview"),
    #path("", view=user_list_view, name="list"),
    #path("~redirect/", view=user_redirect_view, name="redirect"),
    #path("~update/", view=user_update_view, name="update"),
    #path("<str:username>/", view=user_detail_view, name="detail"),
]
