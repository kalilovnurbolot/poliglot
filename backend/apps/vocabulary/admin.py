from django.contrib import admin

from .models import Deck, UserWordProgress, Word


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'owner', 'created_at']
    list_filter = ['language']
    search_fields = ['name']


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['text', 'translation', 'language', 'level', 'part_of_speech', 'owner']
    list_filter = ['language', 'level', 'part_of_speech']
    search_fields = ['text', 'translation']
    filter_horizontal = ['decks']


@admin.register(UserWordProgress)
class UserWordProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'box_level', 'next_review_at', 'last_result']
    list_filter = ['box_level']
