from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Profile
from .sendchamp_service import SendchampService
from .sms_provider import get_sms_service


class AccountsFlowTests(APITestCase):
    def setUp(self):
        self.sms_patcher = patch('accounts.sms_provider.get_sms_service')
        self.mock_sms_service_factory = self.sms_patcher.start()
        self.addCleanup(self.sms_patcher.stop)

        mock_sms_service = type(
            'MockSmsService',
            (),
            {
                'send_verification_code': staticmethod(lambda *args, **kwargs: {'success': True, 'data': {}}),
                'send_password_reset_code': staticmethod(lambda *args, **kwargs: {'success': True, 'data': {}}),
            },
        )()
        self.mock_sms_service_factory.return_value = mock_sms_service

    def test_register_and_verify_phone(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'full_name': 'Ada Lovelace',
                'email': 'ada@example.com',
                'phone_number': '+2348012345678',
                'password': 'StrongPass123',
                'primary_location': 'ilorin',
                'user_type': 'student',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='+2348012345678')
        profile = Profile.objects.get(user=user)
        code = response.data.get('verification_code') or profile.verification_code

        verify_response = self.client.post(
            reverse('accounts:verify-phone'),
            {'user_id': user.id, 'code': code},
            format='json',
        )

        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        self.assertTrue(profile.phone_verified)
        self.assertIn('access_token', verify_response.data)
        self.assertIn('refresh_token', verify_response.data)

    def test_password_reset_flow(self):
        user = User.objects.create_user(
            username='+2348011111111',
            email='reset@example.com',
            password='OldPass123',
        )
        Profile.objects.create(
            user=user,
            phone_number='+2348011111111',
            primary_location='ilorin',
            phone_verified=True,
        )

        request_response = self.client.post(
            reverse('accounts:request-password-reset'),
            {'phone_number': '+2348011111111'},
            format='json',
        )

        self.assertEqual(request_response.status_code, status.HTTP_200_OK)
        reset_code = request_response.data.get('reset_code') or Profile.objects.get(user=user).verification_code

        confirm_response = self.client.post(
            reverse('accounts:confirm-password-reset'),
            {
                'phone_number': '+2348011111111',
                'code': reset_code,
                'new_password': 'NewPass123',
            },
            format='json',
        )

        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewPass123'))

    @override_settings(SMS_PROVIDER='sendchamp')
    def test_sms_provider_defaults_to_sendchamp(self):
        sms_service = get_sms_service()
        self.assertEqual(sms_service.__class__.__name__, 'SendchampService')

    @override_settings(SENDCHAMP_ACCESS_KEY='sendchamp-access', SENDCHAMP_SENDER_ID='CampusDeal')
    @patch('accounts.sendchamp_service.requests.post')
    def test_sendchamp_sms_uses_expected_endpoint(self, mock_post):
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = {'status': True, 'data': {'message_id': 'abc123'}}

        service = SendchampService()
        result = service.send_verification_code('+2348012345678', '123456')

        self.assertTrue(result['success'])
        mock_post.assert_called_once()
        called_url = mock_post.call_args.args[0]
        self.assertEqual(called_url, 'https://api.sendchamp.com/api/v1/sms/send')
