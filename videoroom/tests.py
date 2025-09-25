from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import MeetingRoom, RoomParticipant, ChatMessage


class MeetingRoomModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_room_creation(self):
        """Test creating a meeting room"""
        room = MeetingRoom.objects.create(
            title='Test Room',
            host=self.user
        )
        self.assertEqual(room.title, 'Test Room')
        self.assertEqual(room.host, self.user)
        self.assertTrue(room.room_code)
        self.assertEqual(len(room.room_code), 11)  # XXX-XXX-XXXX format
        self.assertTrue(room.is_active)
        self.assertFalse(room.is_live)

    def test_room_code_generation(self):
        """Test unique room code generation"""
        room1 = MeetingRoom.objects.create(title='Room 1', host=self.user)
        room2 = MeetingRoom.objects.create(title='Room 2', host=self.user)
        
        self.assertNotEqual(room1.room_code, room2.room_code)
        self.assertIsNotNone(room1.room_code)
        self.assertIsNotNone(room2.room_code)

    def test_room_participant_count(self):
        """Test participant count property"""
        room = MeetingRoom.objects.create(title='Test Room', host=self.user)
        self.assertEqual(room.participant_count, 0)
        
        # Add participant
        RoomParticipant.objects.create(room=room, user=self.user)
        self.assertEqual(room.participant_count, 1)

    def test_room_start_meeting(self):
        """Test starting a meeting"""
        room = MeetingRoom.objects.create(title='Test Room', host=self.user)
        self.assertIsNone(room.started_at)
        self.assertFalse(room.is_live)
        
        room.start_meeting()
        self.assertIsNotNone(room.started_at)
        self.assertTrue(room.is_live)

    def test_room_end_meeting(self):
        """Test ending a meeting"""
        room = MeetingRoom.objects.create(title='Test Room', host=self.user)
        room.start_meeting()
        
        room.end_meeting()
        self.assertIsNotNone(room.ended_at)
        self.assertFalse(room.is_active)
        self.assertFalse(room.is_live)


class RoomParticipantModelTest(TestCase):
    def setUp(self):
        self.host = User.objects.create_user(
            username='host',
            email='host@example.com',
            password='hostpass123'
        )
        self.participant = User.objects.create_user(
            username='participant',
            email='participant@example.com',
            password='participantpass123'
        )
        self.room = MeetingRoom.objects.create(
            title='Test Room',
            host=self.host
        )

    def test_participant_creation(self):
        """Test creating a room participant"""
        participant = RoomParticipant.objects.create(
            room=self.room,
            user=self.participant,
            role='participant'
        )
        self.assertEqual(participant.room, self.room)
        self.assertEqual(participant.user, self.participant)
        self.assertEqual(participant.role, 'participant')
        self.assertTrue(participant.is_active)

    def test_participant_display_name(self):
        """Test participant display name property"""
        # Test with user
        participant = RoomParticipant.objects.create(
            room=self.room,
            user=self.participant
        )
        self.assertIn('participant', participant.display_name.lower())
        
        # Test with guest
        guest_participant = RoomParticipant.objects.create(
            room=self.room,
            guest_name='Guest User'
        )
        self.assertEqual(guest_participant.display_name, 'Guest User')

    def test_participant_leave_room(self):
        """Test participant leaving room"""
        participant = RoomParticipant.objects.create(
            room=self.room,
            user=self.participant
        )
        self.assertTrue(participant.is_active)
        self.assertIsNone(participant.left_at)
        
        participant.leave_room()
        self.assertFalse(participant.is_active)
        self.assertIsNotNone(participant.left_at)


class VideoRoomAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_room_api(self):
        """Test creating room via API"""
        url = reverse('videoroom:api_room_list')
        data = {
            'title': 'API Test Room',
            'allow_screen_sharing': True,
            'allow_chat': True,
            'max_participants': 50
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'API Test Room')
        self.assertEqual(response.data['host']['username'], 'testuser')
        self.assertTrue(response.data['allow_screen_sharing'])
        self.assertTrue(response.data['allow_chat'])

    def test_list_rooms_api(self):
        """Test listing rooms via API"""
        # Create a room
        room = MeetingRoom.objects.create(
            title='Test Room',
            host=self.user
        )
        
        url = reverse('videoroom:api_room_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Room')

    def test_join_room_api(self):
        """Test joining room via API"""
        room = MeetingRoom.objects.create(
            title='Test Room',
            host=self.user
        )
        
        url = reverse('videoroom:api_join_room')
        data = {'room_code': room.room_code}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_room_status_api(self):
        """Test room status API"""
        room = MeetingRoom.objects.create(
            title='Test Room',
            host=self.user
        )
        
        url = reverse('videoroom:api_room_status', kwargs={'room_code': room.room_code})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['room_code'], room.room_code)
        self.assertEqual(response.data['title'], 'Test Room')
        self.assertTrue(response.data['is_active'])


class VideoRoomViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.room = MeetingRoom.objects.create(
            title='Test Room',
            host=self.user
        )

    def test_home_view(self):
        """Test home page view"""
        url = reverse('videoroom:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Premium Video Meetings')

    def test_dashboard_view_authenticated(self):
        """Test dashboard view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('videoroom:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back')

    def test_dashboard_view_unauthenticated(self):
        """Test dashboard view redirects unauthenticated user"""
        url = reverse('videoroom:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_create_room_view(self):
        """Test create room view"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('videoroom:create_room')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Meeting Room')

    def test_join_room_view(self):
        """Test join room view"""
        url = reverse('videoroom:join_room_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Join Meeting')

    def test_room_detail_view(self):
        """Test room detail view"""
        url = reverse('videoroom:room_detail', kwargs={'room_code': self.room.room_code})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room.title)

    def test_create_room_post(self):
        """Test creating room via POST"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('videoroom:create_room')
        data = {
            'title': 'New Test Room',
            'allow_screen_sharing': 'on',
            'allow_chat': 'on',
            'max_participants': '100'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Check room was created
        self.assertTrue(MeetingRoom.objects.filter(title='New Test Room').exists())


class ChatMessageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.room = MeetingRoom.objects.create(
            title='Test Room',
            host=self.user
        )
        self.participant = RoomParticipant.objects.create(
            room=self.room,
            user=self.user
        )

    def test_chat_message_creation(self):
        """Test creating a chat message"""
        message = ChatMessage.objects.create(
            room=self.room,
            sender=self.participant,
            message='Hello, world!'
        )
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.sender, self.participant)
        self.assertEqual(message.message, 'Hello, world!')
        self.assertIsNotNone(message.timestamp)

    def test_chat_message_str(self):
        """Test chat message string representation"""
        message = ChatMessage.objects.create(
            room=self.room,
            sender=self.participant,
            message='This is a very long message that should be truncated in the string representation'
        )
        str_repr = str(message)
        self.assertIn(self.participant.display_name, str_repr)
        self.assertIn('This is a very long message that should be', str_repr)