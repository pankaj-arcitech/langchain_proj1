from django.contrib import admin
from .models import Group, DirectThread, Message


# ── Group ──────────────────────────────────────────────────────

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'created_by', 'created_at', 'member_count')
    list_filter   = ('created_at',)
    search_fields = ('name', 'created_by__username')
    filter_horizontal = ('members',)
    readonly_fields   = ('created_at',)

    @admin.display(description='Members')
    def member_count(self, obj):
        return obj.members.count()


# ── Direct Thread ──────────────────────────────────────────────

@admin.register(DirectThread)
class DirectThreadAdmin(admin.ModelAdmin):
    list_display  = ('id', 'participants_display', 'created_at')
    list_filter   = ('created_at',)
    filter_horizontal = ('participants',)
    readonly_fields   = ('created_at',)

    @admin.display(description='Participants')
    def participants_display(self, obj):
        return ' ↔ '.join(u.username for u in obj.participants.all())


# ── Message ────────────────────────────────────────────────────

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ('id', 'chat_type', 'sender', 'short_content', 'is_read', 'created_at')
    list_filter   = ('chat_type', 'is_read', 'created_at')
    search_fields = ('sender__username', 'content')
    readonly_fields   = ('created_at',)
    filter_horizontal = ('tagged_users',)

    @admin.display(description='Content')
    def short_content(self, obj):
        return obj.content[:60] + ('…' if len(obj.content) > 60 else '')
