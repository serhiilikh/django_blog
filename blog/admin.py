from .models import Post, Comment, Profile
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class UserProfileInline(admin.TabularInline):
    model = Profile

class MyUserAdmin(UserAdmin):
    inlines = [
        UserProfileInline,
    ]


admin.site.register(Post)
admin.site.register(Comment)
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)