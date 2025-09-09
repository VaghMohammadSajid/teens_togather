import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging


logger = logging.getLogger(__name__)
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


# test new

from channels.db import database_sync_to_async
class NotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None
        self.user = None
        
    async def connect(self):
        from rest_framework_simplejwt.tokens import AccessToken
        # Get the token from the query string
        token = self.scope['query_string'].decode().split('=')[1]
        logger.debug(f"{token=}")
        try:
            # Decode the access token to get the user
            access_token = AccessToken(token)
            print(access_token,"access_token")
            user_id = access_token['user_id']
            user = await self.get_user(user_id)
            logger.debug(f"{user=}")
            print(user,"user-01")
        except Exception as e:
            # If the token is invalid, close the connection
            print("Invalid token:", e)
            await self.close()
            return

        # Save the user to use later for sending notifications
        self.user = user
        logger.debug(f"{self.user=}")
        # Create a unique group name for the user
        self.group_name = f"user_{self.user.id}"
        logger.debug(f"{self.group_name=}")
        # Add user to the group
        if self.group_name:  # Ensure the group name is valid
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove user from group
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # Handle any messages received from the frontend here
        pass

    # Send a notification to the WebSocket
    async def send_notification(self, event):
        # Send the notification message to the WebSocket
        await self.send(text_data=json.dumps({
            'id': event['message']['id'],
            'message': event['message']['message'],
            'is_read': event['message']['is_read'],
            'created_at': event['message']['created_at'],
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        from Acoounts.models import Accounts
        return Accounts.objects.get(id=user_id)

