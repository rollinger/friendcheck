from django.urls import path

from friendcheck.users.views import (
    user_list_view,
    user_redirect_view,
    user_update_view,
    user_detail_view,
    user_subscription_view,
)

app_name = "users"
urlpatterns = [
    path("", view=user_list_view, name="list"),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("~subscription/", view=user_subscription_view, name="subscription"),
    path("~subscription-success/", view=user_subscription_view, name="subscription-success"),
    path("~subscription-canceled/", view=user_subscription_view, name="subscription-canceled"),
    path("<str:username>/", view=user_detail_view, name="detail"),

]
