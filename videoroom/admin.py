from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import MeetingRoom, RoomParticipant, ChatMessage, RoomRecording


@admin.register(MeetingRoom)
class MeetingRoomAdmin(admin.ModelAdmin):
    list_display = [
        'room_code', 'title', 'host', 'participant_count', 
        'is_live_badge', 'created_at', 'duration_display'
    ]
    list_filter = ['is_active', 'created_at', 'allow_screen_sharing', 'allow_chat']
    search_fields = ['room_code', 'title', 'host__username', 'host__email']
    readonly_fields = ['room_code', 'created_at', 'participant_count', 'duration_minutes']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('room_code', 'title', 'host', 'created_at')
        }),
        ('Room Settings', {
            'fields': (
                'is_active', 'allow_screen_sharing', 'allow_chat', 
                'require_host_approval', 'max_participants'
            )
        }),
        ('Meeting Status', {
            'fields': ('started_at', 'ended_at', 'participant_count', 'duration_minutes')
        }),
    )
    
    def is_live_badge(self, obj):
        if obj.is_live:
            return format_html(
                '<span style="color: #fff; background: #28a745; padding: 2px 8px; border-radius: 12px; font-size: 11px;">🔴 LIVE</span>'
            )
        elif obj.started_at and obj.ended_at:
            return format_html(
                '<span style="color: #fff; background: #6c757d; padding: 2px 8px; border-radius: 12px; font-size: 11px;">ENDED</span>'
            )
        else:
            return format_html(
                '<span style="color: #fff; background: #ffc107; padding: 2px 8px; border-radius: 12px; font-size: 11px;">WAITING</span>'
            )
    is_live_badge.short_description = 'Status'
    
    def duration_display(self, obj):
        if obj.duration_minutes > 0:
            hours, minutes = divmod(obj.duration_minutes, 60)
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return "-"
    duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('host')


@admin.register(RoomParticipant)
class RoomParticipantAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 'room_code', 'role', 'status_badges', 
        'joined_at', 'duration_in_room'
    ]
    list_filter = ['role', 'is_active', 'is_audio_on', 'is_video_on', 'joined_at']
    search_fields = [
        'user__username', 'user__email', 'guest_name', 
        'room__room_code', 'room__title'
    ]
    readonly_fields = ['joined_at', 'left_at']
    
    def room_code(self, obj):
        return obj.room.room_code
    room_code.short_description = 'Room Code'
    
    def status_badges(self, obj):
        badges = []
        if obj.is_active:
            badges.append('<span style="color: #28a745;">🟢 Active</span>')
        else:
            badges.append('<span style="color: #6c757d;">🔴 Left</span>')
            
        if obj.is_audio_on:
            badges.append('🎤')
        else:
            badges.append('🔇')
            
        if obj.is_video_on:
            badges.append('📹')
        else:
            badges.append('📹❌')
            
        if obj.is_screen_sharing:
            badges.append('🖥️')
            
        return format_html(' '.join(badges))
    status_badges.short_description = 'Status'
    
    def duration_in_room(self, obj):
        if obj.joined_at:
            end_time = obj.left_at or timezone.now()
            duration = end_time - obj.joined_at
            minutes = int(duration.total_seconds() / 60)
            if minutes > 60:
                hours, mins = divmod(minutes, 60)
                return f"{hours}h {mins}m"
            return f"{minutes}m"
        return "-"
    duration_in_room.short_description = 'Time in Room'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room', 'user')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender_name', 'room_code', 'message_preview', 'timestamp']
    list_filter = ['timestamp', 'room__room_code']
    search_fields = ['message', 'sender__user__username', 'sender__guest_name']
    readonly_fields = ['timestamp']
    
    def sender_name(self, obj):
        return obj.sender.display_name
    sender_name.short_description = 'Sender'
    
    def room_code(self, obj):
        return obj.room.room_code
    room_code.short_description = 'Room'
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room', 'sender', 'sender__user')


@admin.register(RoomRecording)
class RoomRecordingAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'room_code', 'duration_display', 'file_size_display', 
        'started_at', 'created_at'
    ]
    list_filter = ['created_at', 'started_at']
    search_fields = ['title', 'room__room_code', 'room__title']
    readonly_fields = ['created_at']
    
    def room_code(self, obj):
        return obj.room.room_code
    room_code.short_description = 'Room'
    
    def duration_display(self, obj):
        if obj.duration_seconds > 0:
            hours, remainder = divmod(obj.duration_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            return f"{minutes:02d}:{seconds:02d}"
        return "-"
    duration_display.short_description = 'Duration'
    
    def file_size_display(self, obj):
        if obj.file_size_mb > 0:
            if obj.file_size_mb >= 1024:
                return f"{obj.file_size_mb / 1024:.1f} GB"
            return f"{obj.file_size_mb:.1f} MB"
        return "-"
    file_size_display.short_description = 'File Size'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room')


# Customize admin site headers
admin.site.site_header = 'Meeting App Administration'
admin.site.site_title = 'Meeting App Admin'
admin.site.index_title = 'Welcome to Meeting App Administration'