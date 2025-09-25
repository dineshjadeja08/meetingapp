from django.urls import path
from . import views

app_name = 'videoroom'

urlpatterns = [
    # Template views
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_room, name='create_room'),
    path('join/', views.join_room_page, name='join_room_page'),
    path('room/<str:room_code>/', views.room_detail, name='room_detail'),
    
    # API endpoints
    path('api/rooms/', views.MeetingRoomListCreateView.as_view(), name='api_room_list'),
    path('api/rooms/<str:room_code>/', views.MeetingRoomDetailView.as_view(), name='api_room_detail'),
    path('api/join/', views.join_room, name='api_join_room'),
    path('api/rooms/<str:room_code>/leave/', views.leave_room, name='api_leave_room'),
    path('api/rooms/<str:room_code>/participants/', views.room_participants, name='api_room_participants'),
    path('api/rooms/<str:room_code>/status/', views.update_participant_status, name='api_participant_status'),
    path('api/rooms/<str:room_code>/chat/', views.ChatMessageListCreateView.as_view(), name='api_room_chat'),
    path('api/rooms/<str:room_code>/start/', views.start_meeting, name='api_start_meeting'),
    path('api/rooms/<str:room_code>/end/', views.end_meeting, name='api_end_meeting'),
    path('api/rooms/<str:room_code>/info/', views.room_status, name='api_room_status'),
]