from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MeetingRoom, RoomParticipant, ChatMessage, RoomRecording


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for participants"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        ref_name = 'VideoRoomUser'  # Unique ref_name to avoid conflicts
        
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class RoomParticipantSerializer(serializers.ModelSerializer):
    """Serializer for meeting room participants"""
    user = UserSerializer(read_only=True)
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = RoomParticipant
        fields = [
            'id', 'user', 'guest_name', 'display_name', 'role',
            'is_active', 'is_audio_on', 'is_video_on', 'is_screen_sharing',
            'joined_at', 'left_at'
        ]
        read_only_fields = ['id', 'joined_at', 'left_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    sender = RoomParticipantSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'message', 'timestamp']
        read_only_fields = ['id', 'sender', 'timestamp']


class MeetingRoomSerializer(serializers.ModelSerializer):
    """Serializer for meeting rooms"""
    host = UserSerializer(read_only=True)
    participants = RoomParticipantSerializer(many=True, read_only=True)
    participant_count = serializers.ReadOnlyField()
    is_live = serializers.ReadOnlyField()
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = MeetingRoom
        fields = [
            'id', 'room_code', 'title', 'host', 'is_active',
            'allow_screen_sharing', 'allow_chat', 'require_host_approval',
            'max_participants', 'created_at', 'started_at', 'ended_at',
            'participants', 'participant_count', 'is_live', 'duration_minutes'
        ]
        read_only_fields = [
            'id', 'room_code', 'host', 'created_at', 'started_at', 'ended_at',
            'participants', 'participant_count', 'is_live', 'duration_minutes'
        ]


class CreateMeetingRoomSerializer(serializers.ModelSerializer):
    """Serializer for creating new meeting rooms"""
    
    class Meta:
        model = MeetingRoom
        fields = [
            'title', 'allow_screen_sharing', 'allow_chat', 
            'require_host_approval', 'max_participants'
        ]
    
    def create(self, validated_data):
        validated_data['host'] = self.context['request'].user
        return super().create(validated_data)


class JoinRoomSerializer(serializers.Serializer):
    """Serializer for joining a room"""
    room_code = serializers.CharField(max_length=12)
    guest_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def validate_room_code(self, value):
        try:
            room = MeetingRoom.objects.get(room_code=value, is_active=True)
            self.room = room
            return value
        except MeetingRoom.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive room code.")


class ParticipantStatusSerializer(serializers.Serializer):
    """Serializer for updating participant status"""
    is_audio_on = serializers.BooleanField(required=False)
    is_video_on = serializers.BooleanField(required=False)
    is_screen_sharing = serializers.BooleanField(required=False)


class RoomRecordingSerializer(serializers.ModelSerializer):
    """Serializer for room recordings"""
    
    class Meta:
        model = RoomRecording
        fields = [
            'id', 'title', 'duration_seconds', 'file_size_mb',
            'started_at', 'ended_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']