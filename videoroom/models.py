from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import string
import random

class MeetingRoom(models.Model):
    """
    Video meeting room model - similar to Google Meet rooms
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_code = models.CharField(max_length=12, unique=True, db_index=True)
    title = models.CharField(max_length=200, default="Meeting Room")
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    
    # Room settings
    is_active = models.BooleanField(default=True)
    allow_screen_sharing = models.BooleanField(default=True)
    allow_chat = models.BooleanField(default=True)
    require_host_approval = models.BooleanField(default=False)
    max_participants = models.IntegerField(default=100)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} ({self.room_code})"
    
    @classmethod
    def generate_room_code(cls):
        """Generate a unique room code"""
        while True:
            code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
            code = f"{code[:3]}-{code[3:6]}-{code[6:]}"  # Format: xxx-xxx-xxx
            if not cls.objects.filter(room_code=code).exists():
                return code
    
    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = self.generate_room_code()
        super().save(*args, **kwargs)
    
    @property
    def is_live(self):
        """Check if the meeting is currently live"""
        return (self.is_active and 
                self.started_at and 
                not self.ended_at)
    
    @property
    def duration_minutes(self):
        """Get meeting duration in minutes"""
        if self.started_at:
            end_time = self.ended_at or timezone.now()
            duration = end_time - self.started_at
            return int(duration.total_seconds() / 60)
        return 0
    
    @property
    def participant_count(self):
        """Get current active participant count"""
        return self.participants.filter(is_active=True).count()
    
    def start_meeting(self):
        """Start the meeting"""
        if not self.started_at:
            self.started_at = timezone.now()
            self.save()
    
    def end_meeting(self):
        """End the meeting"""
        if not self.ended_at:
            self.ended_at = timezone.now()
            self.is_active = False
            self.save()
            # Disconnect all participants
            self.participants.update(is_active=False, left_at=timezone.now())


class RoomParticipant(models.Model):
    """
    Participants in a video meeting room
    """
    ROLE_CHOICES = [
        ('host', 'Host'),
        ('co_host', 'Co-Host'),
        ('participant', 'Participant'),
    ]
    
    room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest_name = models.CharField(max_length=100, blank=True)  # For anonymous users
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    
    # Connection status
    is_active = models.BooleanField(default=True)
    is_audio_on = models.BooleanField(default=True)
    is_video_on = models.BooleanField(default=True)
    is_screen_sharing = models.BooleanField(default=False)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['room', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        name = self.user.get_full_name() if self.user else self.guest_name
        return f"{name} in {self.room.room_code}"
    
    @property
    def display_name(self):
        """Get display name for participant"""
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.guest_name or "Guest User"
    
    def leave_room(self):
        """Mark participant as left"""
        self.is_active = False
        self.left_at = timezone.now()
        self.save()


class ChatMessage(models.Model):
    """
    Chat messages in meeting rooms
    """
    room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(RoomParticipant, on_delete=models.CASCADE)
    message = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.display_name}: {self.message[:50]}"


class RoomRecording(models.Model):
    """
    Meeting room recordings (placeholder for future implementation)
    """
    room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, related_name='recordings')
    title = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500, blank=True)
    duration_seconds = models.IntegerField(default=0)
    file_size_mb = models.FloatField(default=0)
    
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Recording: {self.title}"