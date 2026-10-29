from django.contrib import admin

from .models import Booking, ClubSession, Client, InstagramBot, WaitlistEntry


@admin.register(InstagramBot)
class InstagramBotAdmin(admin.ModelAdmin):
    list_display = ['username', 'account_id', 'teacher', 'connected_at']
    exclude = ['access_token']


@admin.register(ClubSession)
class ClubSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'starts_at', 'seats']
    list_filter = ['teacher']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['username', 'instagram_id', 'bot', 'last_message_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['client', 'session', 'status', 'created_at']
    list_filter = ['status']


@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ['client', 'session', 'created_at', 'notified_at']
