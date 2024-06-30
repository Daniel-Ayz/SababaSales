from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
import json
from channels.testing import ChannelsLiveServerTestCase
from .consumers import ChatConsumer
from .api import router
from ninja.testing import TestClient

User = get_user_model()


class ChatConsumerTests(ChannelsLiveServerTestCase):
    def setUp(self):
        # Use sync_to_async to handle the synchronous operations of the ORM
        self.client = TestClient(router)

        self.user = User.objects.create_user(username="testuser", password="password")
        self.channel_layer = get_channel_layer()
        self.room_group_name = (
            f"chat_{self.user.id}"  # Now self.user is properly awaited and instantiated
        )

    async def test_user_connection(self):
        # Create a WebSocket communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
        )
        communicator.scope["user"] = self.user
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        # Disconnect after the test
        await communicator.disconnect()

    async def test_send_message(self):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
        )
        communicator.scope["user"] = self.user
        await communicator.connect()
        message = {"type": "chat_message", "message": "Hello!"}
        # Send a message through the channel layer
        await self.channel_layer.group_send(self.room_group_name, message)
        response = await communicator.receive_json_from()
        self.assertEqual(response, {"type": "chat", "message": "Hello!"})
        await communicator.disconnect()

    async def test_receive_message(self):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
        )
        communicator.scope["user"] = self.user

        await communicator.connect()
        message = {"message": "Hello!"}
        # Simulate sending a message from the client
        await communicator.send_to(json.dumps(message))
        response = await communicator.receive_json_from()
        self.assertEqual(response, {"type": "chat", "message": "Hello!"})
        await communicator.disconnect()

    async def test_disconnect(self):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
        )
        communicator.scope["user"] = self.user

        await communicator.connect()
        await communicator.disconnect()
        # Verify the user is properly disconnected and online count adjusted
        self.user = await sync_to_async(User.objects.get)(id=self.user.id)
        self.assertEqual(self.user.online_count, 0)
