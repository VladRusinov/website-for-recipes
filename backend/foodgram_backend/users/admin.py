from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role'
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    list_editable = ('role',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
