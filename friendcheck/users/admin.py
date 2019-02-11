from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from friendcheck.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (("User", {"fields": ("name", "subscription_type", "subscription_valid_until")}),) \
        + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "name", "is_superuser", "subscription_type", "subscription_valid_until"]
    search_fields = ["name"]
