from django.contrib import admin
from pages.models import NotifySignup


@admin.register(NotifySignup)
class NotifySignupAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    ordering = ('-created_at',)
