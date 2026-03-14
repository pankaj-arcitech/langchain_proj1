from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name       = models.CharField(max_length=100)
    members    = models.ManyToManyField(User, related_name='chat_groups')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DirectThread(models.Model):
    """Represents a 1-to-1 conversation between two users."""
    participants = models.ManyToManyField(User, related_name='direct_threads')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass

    def __str__(self):
        return f"DM: {' <-> '.join(u.username for u in self.participants.all())}"


class Message(models.Model):
    CHAT_TYPE = (
        ('group',  'Group'),
        ('direct', 'Direct'),
    )
    chat_type    = models.CharField(max_length=10, choices=CHAT_TYPE)

    # Only one of these will be set depending on chat_type
    group        = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    direct_thread = models.ForeignKey(DirectThread, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')

    sender       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content      = models.TextField()
    tagged_users = models.ManyToManyField(User, related_name='tagged_in', blank=True)
    is_read      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.chat_type}] {self.sender.username}: {self.content[:50]}"