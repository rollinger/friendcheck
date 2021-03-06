from django.urls import path
from django.views.generic import TemplateView

from facebook.views import (
    facebook_add_datapoint_view,
    facebook_overview_view,
    facebook_friend_view,
#    user_list_view,
#    user_redirect_view,
#    user_update_view,
#    user_detail_view,
)

app_name = "facebook"
urlpatterns = [
    path("", view=facebook_overview_view, name="overview"),
    path("~add_datapoint/", view=facebook_add_datapoint_view, name="add_datapoint"),
    path("friend/<int:pk>/", view=facebook_friend_view, name="friend-detail"),

    #path("", view=user_list_view, name="list"),
    #path("~redirect/", view=user_redirect_view, name="redirect"),
    #path("~update/", view=user_update_view, name="update"),
    #path("<str:username>/", view=user_detail_view, name="detail"),
]
