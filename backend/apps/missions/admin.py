from django.contrib import admin

from .models import Mission, MissionAttempt, MissionStep


class MissionStepInline(admin.StackedInline):
    model = MissionStep
    extra = 0


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'level', 'scene', 'order', 'map_x', 'map_y', 'is_published']
    list_filter = ['language', 'level', 'scene', 'is_published']
    inlines = [MissionStepInline]


@admin.register(MissionAttempt)
class MissionAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'mission', 'total', 'stars', 'finished_at']
    list_filter = ['mission']
