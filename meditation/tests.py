from rest_framework.test import APITestCase, APIClient
from django.shortcuts import reverse
from rest_framework import status
from meditation.models import MeditationCategory, MeditationAudio
from Acoounts.models import Accounts
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from faker import Faker
import os
from django.conf import settings

faker = Faker()


def generate_audio():
    audio = BytesIO()
    audio.write(b"fake audio data")
    audio.seek(0)
    return SimpleUploadedFile("test_audio.mp3", audio.read(), content_type="audio/mpeg")


class MeditationCategoryTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.account = Accounts.objects.create_user(
            username="test@gmail.com",
            email="test@gmail.com",
            phone_number="+91 4242424242",
            designation="DOC",
            password="Test@123",
            first_name="Test",
            last_name="Doctor",
        )
        self.meditation_category = MeditationCategory.objects.create(
            name="first_meditation_category"
        )
        self.meditation_audio = MeditationAudio.objects.create(
            title="first audio",
            audio=generate_audio(),
            category=self.meditation_category,
            created_by=self.account
        )
        self.client.force_authenticate(self.account)

    # Start Meditation Category
    def test_Meditation_Category_create(self):
        url = reverse('create-cate')
        data = {
            'name': 'test',
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])

    def test_Meditation_Category_update(self):
        url = reverse('update-cate', kwargs={'pk': self.meditation_category.id})
        data = {
            'name': 'update_first_meditation_category'
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Meditation Category Updated.")

    def test_Meditation_Category_list(self):
        url = reverse('cate-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MeditationCategory.objects.count(), 1)

    # End Meditation Category

    # Start Stream
    def test_audio_stream_full(self):
        url = reverse('stream', kwargs={'pk': self.meditation_audio.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "audio/mpeg")
        self.assertEqual(int(response["Content-Length"]), self.meditation_audio.audio.size)
        self.assertIn(b"fake audio data", response.streaming_content)

    def test_audio_stream_partial(self):
        url = reverse('stream', kwargs={'pk': self.meditation_audio.pk})
        headers = {"HTTP_RANGE": "bytes=5-"}
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_206_PARTIAL_CONTENT)
        self.assertEqual(response["Content-Type"], "audio/mpeg")
        self.assertIn("Content-Range", response)
        self.assertTrue(response["Content-Range"].startswith("bytes 5-"))

    def test_audio_not_found(self):
        url = reverse('stream', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Audio file not found")

    # End Stream

    # Start Meditation Audio
    def test_meditation_audio_create(self):
        url = reverse('create-audio')
        data = {
            'title': 'first title',
            'audio': generate_audio(),
            'category': self.meditation_category.id,
            'created_by': self.account.id
        }
        resp = self.client.post(url, data, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['title'], 'first title')
        self.assertEqual(resp.data['category_by_name'], self.meditation_category.name)
        self.assertEqual(resp.data['created_by_name'], self.account.username)

    def test_meditation_audio_list(self):
        url = reverse('list-audio')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(MeditationAudio.objects.count(), 1)

    def test_meditation_audio_bad_request(self):
        url = reverse('your-model-delete', kwargs={'pk': 12})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_meditation_audio_delete(self):
        url = reverse('your-model-delete', kwargs={'pk': self.meditation_category.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Meditation Category deleted successfully.")

    # End Meditation audio
    def tearDown(self):
        Accounts.objects.all().delete()
        MeditationCategory.objects.all().delete()
        MeditationAudio.objects.all().delete()
