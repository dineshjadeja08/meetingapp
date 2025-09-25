from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import MeetingRoom, RoomParticipant, ChatMessage, RoomRecording
from .serializers import (
    MeetingRoomSerializer, CreateMeetingRoomSerializer, JoinRoomSerializer,
    RoomParticipantSerializer, ChatMessageSerializer, ParticipantStatusSerializer,
    RoomRecordingSerializer
)


class MeetingRoomListCreateView(generics.ListCreateAPIView):
    """
    List user's meeting rooms or create a new one
    """
    serializer_class = MeetingRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return MeetingRoom.objects.filter(
            Q(host=user) | Q(participants__user=user)
        ).distinct().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateMeetingRoomSerializer
        return MeetingRoomSerializer
    
    @swagger_auto_schema(
        operation_description="Create a new meeting room",
        responses={201: MeetingRoomSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        
        # Return the full room data using MeetingRoomSerializer
        response_serializer = MeetingRoomSerializer(room)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class MeetingRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a meeting room
    """
    serializer_class = MeetingRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'room_code'
    
    def get_queryset(self):
        return MeetingRoom.objects.filter(host=self.request.user)


@swagger_auto_schema(
    method='post',
    request_body=JoinRoomSerializer,
    responses={
        200: RoomParticipantSerializer,
        400: 'Invalid room code or room is full',
        403: 'Host approval required'
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow anonymous users
def join_room(request):
    """
    Join a meeting room by room code
    """
    serializer = JoinRoomSerializer(data=request.data)
    if serializer.is_valid():
        room = serializer.room
        user = request.user if request.user.is_authenticated else None
        guest_name = serializer.validated_data.get('guest_name', '')
        
        # Check if room is full
        if room.participant_count >= room.max_participants:
            return Response(
                {'error': 'Meeting room is full'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already in room
        if user:
            participant, created = RoomParticipant.objects.get_or_create(
                room=room, user=user,
                defaults={'role': 'host' if room.host == user else 'participant'}
            )
            if not created and participant.is_active:
                return Response(
                    {'error': 'You are already in this room'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            participant.is_active = True
            participant.save()
        else:
            # Anonymous user
            if not guest_name:
                return Response(
                    {'error': 'Guest name is required for anonymous users'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            participant = RoomParticipant.objects.create(
                room=room, guest_name=guest_name, role='participant'
            )
        
        # Start meeting if host joins
        if user == room.host:
            room.start_meeting()
        
        serializer = RoomParticipantSerializer(participant)
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    responses={200: 'Successfully left the room'}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_room(request, room_code):
    """
    Leave a meeting room
    """
    room = get_object_or_404(MeetingRoom, room_code=room_code, is_active=True)
    try:
        participant = RoomParticipant.objects.get(room=room, user=request.user, is_active=True)
        participant.leave_room()
        
        # End meeting if host leaves
        if request.user == room.host:
            room.end_meeting()
        
        return Response({'message': 'Successfully left the room'})
    except RoomParticipant.DoesNotExist:
        return Response(
            {'error': 'You are not in this room'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@swagger_auto_schema(
    method='get',
    responses={200: RoomParticipantSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def room_participants(request, room_code):
    """
    Get list of participants in a room
    """
    room = get_object_or_404(MeetingRoom, room_code=room_code, is_active=True)
    participants = room.participants.filter(is_active=True)
    serializer = RoomParticipantSerializer(participants, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='patch',
    request_body=ParticipantStatusSerializer,
    responses={200: RoomParticipantSerializer}
)
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_participant_status(request, room_code):
    """
    Update participant's audio/video/screen sharing status
    """
    room = get_object_or_404(MeetingRoom, room_code=room_code, is_active=True)
    participant = get_object_or_404(
        RoomParticipant, room=room, user=request.user, is_active=True
    )
    
    serializer = ParticipantStatusSerializer(data=request.data)
    if serializer.is_valid():
        for field, value in serializer.validated_data.items():
            setattr(participant, field, value)
        participant.save()
        
        response_serializer = RoomParticipantSerializer(participant)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatMessageListCreateView(generics.ListCreateAPIView):
    """
    List chat messages or send a new message
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        room_code = self.kwargs['room_code']
        room = get_object_or_404(MeetingRoom, room_code=room_code, is_active=True)
        return room.chat_messages.all()
    
    def perform_create(self, serializer):
        room_code = self.kwargs['room_code']
        room = get_object_or_404(MeetingRoom, room_code=room_code, is_active=True)
        participant = get_object_or_404(
            RoomParticipant, room=room, user=self.request.user, is_active=True
        )
        serializer.save(room=room, sender=participant)


@swagger_auto_schema(
    method='post',
    responses={200: 'Meeting started successfully'}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_meeting(request, room_code):
    """
    Start a meeting (only host can do this)
    """
    room = get_object_or_404(
        MeetingRoom, room_code=room_code, host=request.user, is_active=True
    )
    room.start_meeting()
    return Response({'message': 'Meeting started successfully'})


@swagger_auto_schema(
    method='post',
    responses={200: 'Meeting ended successfully'}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def end_meeting(request, room_code):
    """
    End a meeting (only host can do this)
    """
    room = get_object_or_404(
        MeetingRoom, room_code=room_code, host=request.user, is_active=True
    )
    room.end_meeting()
    return Response({'message': 'Meeting ended successfully'})


@swagger_auto_schema(
    method='get',
    responses={200: 'Room status information'}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def room_status(request, room_code):
    """
    Get room status and basic information
    """
    room = get_object_or_404(MeetingRoom, room_code=room_code)
    
    return Response({
        'room_code': room.room_code,
        'title': room.title,
        'is_active': room.is_active,
        'is_live': room.is_live,
        'participant_count': room.participant_count,
        'max_participants': room.max_participants,
        'allow_chat': room.allow_chat,
        'allow_screen_sharing': room.allow_screen_sharing,
        'require_host_approval': room.require_host_approval,
        'duration_minutes': room.duration_minutes
    })


# Template views for frontend
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home(request):
    """Home page with option to create or join a room"""
    return render(request, 'videoroom/home.html')


@login_required
def dashboard(request):
    """User dashboard showing their rooms"""
    user_rooms = MeetingRoom.objects.filter(host=request.user).order_by('-created_at')[:10]
    recent_participations = RoomParticipant.objects.filter(
        user=request.user
    ).select_related('room').order_by('-joined_at')[:10]
    
    context = {
        'user_rooms': user_rooms,
        'recent_participations': recent_participations,
    }
    return render(request, 'videoroom/dashboard.html', context)


@login_required
def create_room(request):
    """Create a new meeting room"""
    if request.method == 'POST':
        title = request.POST.get('title', 'New Meeting')
        allow_screen_sharing = request.POST.get('allow_screen_sharing') == 'on'
        allow_chat = request.POST.get('allow_chat') == 'on'
        require_host_approval = request.POST.get('require_host_approval') == 'on'
        max_participants = int(request.POST.get('max_participants', 100))
        
        room = MeetingRoom.objects.create(
            title=title,
            host=request.user,
            allow_screen_sharing=allow_screen_sharing,
            allow_chat=allow_chat,
            require_host_approval=require_host_approval,
            max_participants=max_participants
        )
        
        messages.success(request, f'Meeting room created! Room code: {room.room_code}')
        return redirect('videoroom:room_detail', room_code=room.room_code)
    
    return render(request, 'videoroom/create_room.html')


def join_room_page(request):
    """Join room page"""
    if request.method == 'POST':
        room_code = request.POST.get('room_code')
        guest_name = request.POST.get('guest_name', '')
        
        try:
            room = MeetingRoom.objects.get(room_code=room_code, is_active=True)
            return redirect('videoroom:room_detail', room_code=room_code)
        except MeetingRoom.DoesNotExist:
            messages.error(request, 'Invalid room code or room is inactive.')
    
    return render(request, 'videoroom/join_room.html')


def room_detail(request, room_code):
    """Meeting room detail page (the actual video call interface)"""
    try:
        room = MeetingRoom.objects.get(room_code=room_code)
        
        # Check if user can access the room
        can_access = (
            room.is_active or 
            (request.user.is_authenticated and request.user == room.host)
        )
        
        if not can_access:
            messages.error(request, 'This meeting room is not accessible.')
            return redirect('videoroom:home')
        
        context = {
            'room': room,
            'is_host': request.user.is_authenticated and request.user == room.host,
        }
        return render(request, 'videoroom/room_detail.html', context)
        
    except MeetingRoom.DoesNotExist:
        messages.error(request, 'Meeting room not found.')
        return redirect('videoroom:home')