from django.contrib import admin

from .models import GrammarProgress, GrammarRule


@admin.register(GrammarRule)
class GrammarRuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'level', 'order']
    list_filter = ['language', 'level']
    search_fields = ['title', 'body']


@admin.register(GrammarProgress)
class GrammarProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'rule', 'learned_at']
    list_filter = ['rule__language']
