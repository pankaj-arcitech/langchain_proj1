from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Group, DirectThread, Message
from .serializers import (
    CreateGroupSerializer,
    GroupMemberActionSerializer,
    SearchQuerySerializer,
)


# ── Group Chat Views ──────────────────────────────────────────

class GroupMessagesView(APIView):
    """Fetch paginated message history for a group."""
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id, members=request.user)
        msgs = (
            group.messages
            .select_related('sender')
            .prefetch_related('tagged_users')
            .order_by('-created_at')[:50]
        )
        data = [
            {
                'id':           m.id,
                'sender':       m.sender.username,
                'content':      m.content,
                'tagged_users': [u.username for u in m.tagged_users.all()],
                'created_at':   str(m.created_at),
            }
            for m in reversed(list(msgs))
        ]
        return Response({'messages': data})


class CreateGroupView(APIView):
    """Create a new group and add the creator as a member."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateGroupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name       = serializer.validated_data['name']
        member_ids = serializer.validated_data['member_ids']

        group = Group.objects.create(name=name, created_by=request.user)
        group.members.add(request.user, *User.objects.filter(id__in=member_ids))
        return Response({'group_id': group.id, 'name': group.name}, status=status.HTTP_201_CREATED)


class GroupMemberView(APIView):
    """Add or remove a member from a group (only creator can do this)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id, action):
        if action not in ('add', 'remove'):
            return Response({'error': 'Invalid action. Use "add" or "remove".'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GroupMemberActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group, id=group_id, created_by=request.user)
        user  = get_object_or_404(User, id=serializer.validated_data['user_id'])

        if action == 'add':
            group.members.add(user)
            return Response({'status': 'added', 'username': user.username})

        group.members.remove(user)
        return Response({'status': 'removed', 'username': user.username})


# ── Direct Chat Views ─────────────────────────────────────────

class DirectThreadView(APIView):
    """Get existing DM thread or create a new one between two users."""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)

        if other_user == request.user:
            return Response(
                {'error': 'Cannot start a chat with yourself.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        thread = (
            DirectThread.objects
            .filter(participants=request.user)
            .filter(participants=other_user)
            .first()
        )

        if not thread:
            thread = DirectThread.objects.create()
            thread.participants.add(request.user, other_user)

        return Response({'thread_id': thread.id})


class DirectMessagesView(APIView):
    """Fetch paginated message history for a DM thread."""
    permission_classes = [IsAuthenticated]

    def get(self, request, thread_id):
        thread = get_object_or_404(DirectThread, id=thread_id, participants=request.user)
        msgs = (
            thread.messages
            .select_related('sender')
            .order_by('-created_at')[:50]
        )
        data = [
            {
                'id':         m.id,
                'sender':     m.sender.username,
                'content':    m.content,
                'is_read':    m.is_read,
                'created_at': str(m.created_at),
            }
            for m in reversed(list(msgs))
        ]
        return Response({'messages': data})


# ── Shared Utility ────────────────────────────────────────────

class SearchUsersView(APIView):
    """Autocomplete endpoint for @mention tagging."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = SearchQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data['q']
        if not query:
            return Response([])

        users = (
            User.objects
            .filter(username__istartswith=query)
            .exclude(id=request.user.id)
            .values('id', 'username')[:10]
        )
        return Response(list(users))