from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from Acoounts.models import Notification
from django.contrib.auth.models import User
import logging


logger = logging.getLogger(__name__)

def send_notification(user, message):
    logger.debug(f"{user=}")
    logger.debug(f"{message=}")

    # Save notification to the database
    notification = Notification.objects.create(user=user, message=message)
    logger.debug(f"{notification=}")

    # Send notification via WebSocket
    channel_layer = get_channel_layer()

    # Send the notification to the specific user (using their user ID in the channel name)
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",  # Group name is based on the user ID
        {
            "type": "send_notification",  # This will trigger the 'send_notification' method in the consumer
            "message": {
                "id": notification.id,  # Include the notification ID (optional)
                "message": notification.message,  # Send the message text
                "is_read": notification.is_read,  # Send the read status (optional)
                "created_at": notification.created_at.isoformat(),  # Send the creation timestamp (optional)
            }
        }
    )
