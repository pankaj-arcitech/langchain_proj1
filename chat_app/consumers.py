import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Group, DirectThread, Message
from ai_app.consumers import get_user_from_token
from urllib.parse import parse_qs


class GroupChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Extract query parameters
        query_string = self.scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        
        # Get token
        self.jwt_token = params.get('token', [None])[0]
        if not self.jwt_token:
            await self.close(code=4001)
            return
        self.user = await get_user_from_token(self.jwt_token)

        self.group_id = params.get('group_id', [None])[0]
        self.room_group = f'group_{self.group_id}'

        # Reject if user is not a member
        is_member = await self.check_group_membership()
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data    = json.loads(text_data)
        content = data.get('message', '').strip()
        user    = self.user

        if not content:
            return

        tagged_usernames = re.findall(r'@(\w+)', content)
        tagged_users     = await self.get_tagged_users(tagged_usernames)
        msg              = await self.save_group_message(user, content, tagged_users)

        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':         'chat_message',
                'message_id':   msg.id,
                'message':      content,
                'sender':       user.username,
                'tagged_users': tagged_usernames,
                'created_at':   str(msg.created_at),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # ---- DB helpers ----

    @database_sync_to_async
    def check_group_membership(self):
        return Group.objects.filter(id=self.group_id, members=self.user).exists()

    @database_sync_to_async
    def get_tagged_users(self, usernames):
        return list(User.objects.filter(username__in=usernames))

    @database_sync_to_async
    def save_group_message(self, user, content, tagged_users):
        group = Group.objects.get(id=self.group_id)
        msg   = Message.objects.create(
            chat_type='group',
            group=group,
            sender=user,
            content=content,
        )
        if tagged_users:
            msg.tagged_users.set(tagged_users)
        return msg


class DirectChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Extract query parameters
        query_string = self.scope.get('query_string', b'').decode()
        params = parse_qs(query_string)

        # Get token
        self.jwt_token = params.get('token', [None])[0]

        if not self.jwt_token:
            await self.close(code=4001)
            return
        self.user = await get_user_from_token(self.jwt_token)

        self.thread_id = params.get('thread_id', [None])[0]
        self.room_group = f'direct_{self.thread_id}'

        # Reject if user is not a participant
        is_participant = await self.check_participation()
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        # Mark all unread messages as read on connect
        await self.mark_messages_read()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data    = json.loads(text_data)
        content = data.get('message', '').strip()
        user    = self.user

        if not content:
            return

        msg = await self.save_direct_message(user, content)

        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':       'chat_message',
                'message_id': msg.id,
                'message':    content,
                'sender':     user.username,
                'created_at': str(msg.created_at),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # ---- DB helpers ----

    @database_sync_to_async
    def check_participation(self):
        return DirectThread.objects.filter(id=self.thread_id, participants=self.user).exists()

    @database_sync_to_async
    def save_direct_message(self, user, content):
        thread = DirectThread.objects.get(id=self.thread_id)
        return Message.objects.create(
            chat_type='direct',
            direct_thread=thread,
            sender=user,
            content=content,
        )

    @database_sync_to_async
    def mark_messages_read(self):
        Message.objects.filter(
            direct_thread_id=self.thread_id,
            is_read=False,
        ).exclude(sender=self.user).update(is_read=True)