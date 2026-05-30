from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile
from communication.models import Chat, ModeratedMessageLog
from marketplace.models import ItemCategory, ItemListing


class CommunicationModerationTests(APITestCase):
    def setUp(self):
        self.user_one = User.objects.create_user(
            username='+2348012222221',
            email='one@example.com',
            password='StrongPass123',
        )
        self.user_two = User.objects.create_user(
            username='+2348012222222',
            email='two@example.com',
            password='StrongPass123',
        )
        Profile.objects.create(
            user=self.user_one,
            phone_number='+2348012222221',
            primary_location='ilorin',
            phone_verified=True,
        )
        Profile.objects.create(
            user=self.user_two,
            phone_number='+2348012222222',
            primary_location='ilorin',
            phone_verified=True,
        )
        category = ItemCategory.objects.create(name='Books', icon='book')
        item = ItemListing.objects.create(
            seller=self.user_one,
            title='Physics Textbook',
            description='Latest edition',
            category=category,
            condition='used',
            price='5000.00',
            location='ilorin',
        )
        self.chat = Chat.objects.create(
            participant_1=self.user_one,
            participant_2=self.user_two,
            related_item=item,
        )

    def test_phone_number_sharing_is_blocked(self):
        self.client.force_authenticate(user=self.user_one)
        response = self.client.post(
            reverse('communication:send-message', kwargs={'chat_id': self.chat.id}),
            {'text': 'Call me on 08012345678'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(ModeratedMessageLog.objects.filter(chat=self.chat).exists())
        self.user_one.profile.refresh_from_db()
        self.assertEqual(self.user_one.profile.chat_strikes, 1)
