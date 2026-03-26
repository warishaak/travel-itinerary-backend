from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["email", "first_name", "last_name", "is_staff"]
    ordering = ["email"]
    fieldsets = UserAdmin.fieldsets
