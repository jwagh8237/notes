from django.contrib import admin

from .models import Category, Note


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'owner__username']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'owner',
        'category',
        'priority',
        'is_pinned',
        'is_archived',
        'updated_at',
    ]
    list_filter = ['priority', 'is_pinned', 'is_archived', 'category']
    search_fields = ['title', 'body', 'tags', 'owner__username']
