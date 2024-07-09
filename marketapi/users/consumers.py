import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import CustomUser, Notification
from typing import List
from .schemas import NotificationSchema
from django.db import transaction


# Channel layer - a global variable that allows us to send messages to specific channels
channel_layer = get_channel_layer()


# Insure that all users online counter is 0 at the start of the server
def reset_all_online_count():
    # pass
    users = CustomUser.objects.all()
    for user in users:
        user.online_count = 0
        user.save()
    print("All users online count reset to 0")


def _get_unseen_notifications(user_id: int) -> List[NotificationSchema]:
    user = CustomUser.objects.get(id=user_id)
    notifications = Notification.objects.filter(user=user, seen=False)
    return notifications


def _mark_notification_as_seen(notification_id: int):
    notification = Notification.objects.get(id=notification_id)
    notification.seen = True
    notification.save()


# Functions to send messages to a specific user
#   - Each user is in a group named 'chat_{user_id}'
#   ! can also send messages to ALL anonymous users -> when user_id == 'anonymous'
def send_message_to_user(user_id, message, notification_id=-1, sent_by="System"):
    async_to_sync(channel_layer.group_send)(
        f"chat_{user_id}",
        {
            "type": "chat_message",
            "message": message,
            "sent_by": sent_by,
            "notification_id": notification_id,
        },
    )


def update_user_increment_online_count(user_id):
    with transaction.atomic():
        user = CustomUser.objects.get(id=user_id)
        user.online_count += 1
        user.save()
        # print(f"User {user.username} online count: {user.online_count}")


def update_user_decrement_online_count(user_id):
    with transaction.atomic():
        user = CustomUser.objects.get(id=user_id)
        user.online_count -= 1
        user.save()
        # print(f"User {user.username} online count: {user.online_count}")


# This is the consumer that will handle the websocket connection
class ChatConsumer(WebsocketConsumer):
    # This function is called when a new connection is made
    def connect(self):
        # self.room_group_name = "test"
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_group_name = f"chat_{self.user.id}"
            update_user_increment_online_count(self.user.id)
        else:
            self.room_group_name = "chat_anonymous"
        # print(f"New Connection: {self.room_group_name}")

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

        # Banner for new chat
        # FOR TESTING PURPOSES
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,
        #     {
        #         "type": "chat_message",
        #         "message": f"YOU ARE CONNECTED TO {self.room_group_name}",
        #     },
        # )

        if self.user.is_authenticated:
            # Send all notifications that haven't been 'seen' in the database
            from .usercontroller import UserController

            notifications = _get_unseen_notifications(self.user.id)
            for notification in notifications:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": notification.message,
                        "notification_id": notification.id,
                        "sent_by": notification.sent_by,
                    },
                )
                # _mark_notification_as_seen(notification.id)

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            update_user_decrement_online_count(self.user.id)
        # print(f"Disconnected: {self.room_group_name}")
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # This function is called when a new message is received from the client
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sent_by": self.user.username,
                "notification_id": -1,
            },
        )

    # This function is called when a message is sent to the group
    def chat_message(self, event):
        message = event["message"]
        sent_by = event["sent_by"]
        notification_id = event["notification_id"]

        self.send(
            text_data=json.dumps(
                {
                    "type": "chat",
                    "message": message,
                    "sent_by": sent_by,
                    "notification_id": notification_id,
                }
            )
        )
