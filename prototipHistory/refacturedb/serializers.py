from django.contrib.auth.models import User
from rest_framework import serializers

from refacturedb.models import *

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('room', 'user', 'contact', 'text', 'seen')

class RoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ('user', 'contact', 'queue', 'custom_fields', 'urn', 'callback_url', 'ended_at', 'ended_by', 'is_active', 'is_waiting', 'transfer_history', 'messages')
