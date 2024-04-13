from django.contrib import admin

from apps.users import models
from django.contrib.auth.models import Group
from allauth.socialaccount.models import SocialApp, SocialToken, SocialAccount
from django.contrib.sites.models import Site
from django.contrib.auth.admin import UserAdmin
from apps.users.forms import CustomUserChangeForm, CustomUserCreationForm


# admin.site.unregister(Group)
# admin.site.unregister(SocialApp)
# admin.site.unregister(SocialToken)
# admin.site.unregister(Site)
# admin.site.unregister(SocialAccount)


@admin.register(models.CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_director', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('is_staff', 'is_superuser',)
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)
    empty_value_display = '-empty-'
