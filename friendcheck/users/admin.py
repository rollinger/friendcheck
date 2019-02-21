import random, string
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from . models import Configuration

from friendcheck.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (("User", {"fields": ("name", "invite_code", "subscription_type", "subscription_valid_until")}),) \
        + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "name", "is_superuser", "subscription_type", "subscription_valid_until"]
    search_fields = ["name"]



@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ["key", "value",]
    list_display_links = ['key']

    actions = ['generate_new_invite_codes']

    def generate_new_invite_codes(self, request, queryset):
        n = 10
        invite_codes = queryset[0]
        if invite_codes.key == "INVITE_CODES":
            new_codes = ""
            for _ in range(n):
                ic = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                new_codes += ", " + ic
            invite_codes.value += new_codes
            #print(new_codes)
            invite_codes.save()
        #
    generate_new_invite_codes.short_description = "Generates 10 new Invite Codes"
