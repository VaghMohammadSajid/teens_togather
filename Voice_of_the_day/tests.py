import logging
from django.urls import reverse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from Voice_of_the_day.models import VoiceOfTheDay, Concentrate, TeenagerAndParent
from Acoounts.models import Accounts
from faker import Faker
from io import BytesIO
from PIL import Image
import os
from unittest.mock import patch

logger = logging.getLogger(__name__)
faker = Faker()


def generate_test_image():
    image = Image.new('RGB', (100, 100), color=(255, 0, 0))
    image_io = BytesIO()
    image.save(image_io, format='JPEG')
    image_io.seek(0)
    return SimpleUploadedFile("test_image.jpg", image_io.read(), content_type="image/jpeg")


class VoiceAPiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.account = Accounts.objects.create_user(
            email="admin@gmail.com",
            password="admin",
            first_name="Admin",
            last_name="Sharma",
            username="Test@gmail.com",
            phone_number="+91 8888888888",
            designation="ADMIN",
        )
        self.account.is_staff = True
        self.account.save()

        self.concentrate = Concentrate.objects.create(
            name=faker.name(),
        )

        self.teenandparent = TeenagerAndParent.objects.create(
            account=self.account,
            date_of_birth=faker.date(),
            gender=faker.random.choice(['Male', 'Female']),
        )
        self.teenandparent.concentrate_on.set([self.concentrate])

        self.voice_data = VoiceOfTheDay.objects.create(
            title="first voice",
            content="this is testing",
            total_likes=4,
        )
        self.voice_data.concentrates.set([self.concentrate])
        self.voice_data.person_likes.set([self.teenandparent])

        self.client.force_authenticate(user=self.account)

    def test_create_voice_day(self):
        url = reverse('voice-create')

        image = generate_test_image()

        data = {
            "title": "first voice",
            "content": "this is testing",
            "image": image,
            "concentrates": [self.concentrate.id],
            "person_likes": [self.teenandparent.id],
            "total_likes": "4",
            "publish_by": self.account
        }

        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VoiceOfTheDay.objects.count(), 2)

        voice_instance = VoiceOfTheDay.objects.last()
        self.assertIsNotNone(voice_instance.image)
        self.assertTrue(os.path.isfile(voice_instance.image.path))

    def test_update_voice_day(self):
        url = reverse('voice-update', kwargs={'pk': self.voice_data.pk})
        image = generate_test_image()
        data = {
            "title": "first update voice",
            "content": "this is testing for update",
            "image": image,
            "concentrates": [self.concentrate.id],
            "person_likes": [self.teenandparent.id],
            "total_likes": "10",
        }
        response = self.client.put(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.voice_data.refresh_from_db()
        self.assertEqual(self.voice_data.title, "first update voice")

    def test_list_voice_day(self):
        url = reverse('voice-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    # Start Voice delete
    def test_delete_voice_day(self):
        url = reverse('voice-delete', kwargs={'pk': self.voice_data.pk})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(VoiceOfTheDay.objects.filter(pk=self.voice_data.pk).exists())

        if self.voice_data.image:
            self.assertFalse(os.path.isfile(self.voice_data.image.path), "The image file was not deleted.")

    @patch('rest_framework.generics.DestroyAPIView.get_object')
    def test_voice_delete_exception_handling(self, mock_get_object):
        mock_get_object.side_effect = Exception("Simulated exception")

        url = reverse('voice-delete', kwargs={'pk': 1})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Simulated exception')

    @patch('rest_framework.generics.DestroyAPIView.get_object')
    def test_voice_of_the_day_delete_does_not_exist(self, mock_get_object):
        mock_get_object.side_effect = VoiceOfTheDay.DoesNotExist

        url_delete = reverse('voice-delete', kwargs={'pk': 1})
        response_delete = self.client.delete(url_delete)
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('message', response_delete.data)
        self.assertEqual(response_delete.data['message'], 'Voice of the Day not found.')
    # End Voice Delete

    @patch('rest_framework.generics.RetrieveUpdateAPIView.get_object')
    def test_voice_of_the_day_update_does_not_exist(self, mock_get_object):
        mock_get_object.side_effect = VoiceOfTheDay.DoesNotExist

        url_put = reverse('voice-update', kwargs={'pk': 1})
        response_put = self.client.put(url_put, data={'concentrates': [1, 2]}, format='json')
        self.assertEqual(response_put.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response_put.data)
        self.assertEqual(response_put.data['error'], 'Voice Not Found.')

    # Start voice_like
    def test_voice_of_the_day_like(self):
        url = reverse('voice-like')
        response = self.client.post(url, {"id": self.voice_data.pk})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)

        self.voice_data.refresh_from_db()
        self.assertEqual(self.voice_data.total_likes, 3)

        response = self.client.post(url, {"id": self.voice_data.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)

        self.voice_data.refresh_from_db()
        self.assertEqual(self.voice_data.total_likes, 4)

    def test_voice_of_the_day_like_does_not_exist(self):
        url_post = reverse('voice-like')
        response_post = self.client.post(url_post, data={'post_id': 999}, format='json')
        self.assertEqual(response_post.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('msg', response_post.data)
        self.assertEqual(response_post.data['msg'], 'post with this id not found')

    @patch('Acoounts.models.TeenagerAndParent.objects.get')
    def test_voice_like_in_teens_and_parent_does_not_exist(self, mock_get_object):
        mock_get_object.side_effect = TeenagerAndParent.DoesNotExist

        url = reverse('voice-like')
        response = self.client.post(url, {"id": self.voice_data.pk})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('msg', response.data)
        self.assertEqual(response.data['msg'], 'User is not Teens or Parent')
    # End voice_like

    def tearDown(self):
        for voice in VoiceOfTheDay.objects.all():
            if voice.image and os.path.isfile(voice.image.path):
                os.remove(voice.image.path)
        VoiceOfTheDay.objects.all().delete()
        TeenagerAndParent.objects.all().delete()
        Concentrate.objects.all().delete()
        Accounts.objects.all().delete()
        super().tearDown()
