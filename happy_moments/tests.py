from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from happy_moments.models import HappyMoments
from Acoounts.models import TeenagerAndParent, Accounts, Avatar
from faker import Faker
from django.urls import reverse
import os
from datetime import datetime
fake = Faker()

class HAppyMomentApiTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = Accounts.objects.create_user(
            username="test@gmail.com",
            email="test@gmail.com",
            phone_number="+91 4242424242",
            designation="Teens",
            password="Test@123",
            first_name="Test",
            last_name="Teens",
        )
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()

        self.avatar = Avatar.objects.create(image="Test.jpg")

        self.teenandparent = TeenagerAndParent.objects.create(
            account=self.user,
            avatar=self.avatar,
            nick_name="nick",
            date_of_birth=fake.date(),
            gender=fake.random.choice(['Male', 'Female']),
        )
        self.happy_moment_1 = HappyMoments.objects.create(
            title="Happy Moment 1",
            file="test_image_1.jpg",
            total_likes=0,
            status=True,
            publish_by=self.teenandparent,
        )
        self.happy_moment_1.person_likes.set([self.teenandparent])
        self.happy_moment_1.save()
        self.happy_moment_2 = HappyMoments.objects.create(
            title="Happy Moment 2",
            file="test_image_2.jpg",
            total_likes=0,
            status=True,
            publish_by=self.teenandparent,
        )
        self.happy_moment_2.person_likes.set([self.teenandparent])
        self.happy_moment_2.save()

        self.valid_file = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        self.client.force_authenticate(self.user)

    # Start Create
    def test_happy_create_valid_data(self):
        url = reverse("create")

        data = {
            "title": "Happy Moment",
            "file": self.valid_file,
            "person_likes": [self.teenandparent.id],
            "total_likes": 1,
            "status": True
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["title"], "Happy Moment")
        self.assertEqual(response.data["publish_by"], "nick")
        self.assertEqual(response.data["person_likes"], [])

        self.assertEqual(HappyMoments.objects.count(), 3)
        happy_moment = HappyMoments.objects.first()
        self.assertEqual(happy_moment.title, "Happy Moment 1")
        self.assertEqual(happy_moment.publish_by, self.teenandparent)

    def test_happy_create_invalid_file_type(self):
        url = reverse("create")
        invalid_file = SimpleUploadedFile(
            "test_file mov.", b"invalid_content", content_type="text/plain"
        )

        data = {
            "title": "Invalid File Test",
            "file": invalid_file,

        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)
        self.assertEqual(HappyMoments.objects.count(), 2)

    def test_happy_create_without_authentication(self):
        url = reverse("create")
        self.client.logout()
        data = {
            "title": "Unauthenticated Test",
            "file": self.valid_file,
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(HappyMoments.objects.count(), 2)
    # End Create

    # Start List
    def test_happy_list_authenticated(self):
        url = reverse('list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertIn("id", response.data['results'][0])
        self.assertEqual(response.data['results'][0]["title"], "Happy Moment 2")
        self.assertEqual(response.data['results'][1]["title"], "Happy Moment 1")

    def test_happy_list_authenticated_with_search(self):
        url = reverse('list')
        response = self.client.get(url + "?search=Happy Moment 1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data['results'][0]["title"], "Happy Moment 1")

    def test_happy_list_unauthenticated(self):
        url = reverse('list')

        self.client.logout()
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_in_serializer_context(self):
        url = reverse('list')

        response = self.client.get(url)
        print("response is :", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        self.assertEqual(response.data['count'], HappyMoments.objects.count())
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        results = response.data['results']
        self.assertEqual(len(results), 2)

        result = results[0]
        self.assertIn('id', result)
        self.assertIn('is_liked', result)
        self.assertIn('publish_by', result)
        self.assertIn('person_likes', result)
        self.assertIn('title', result)
        self.assertIn('file', result)
        self.assertIn('total_likes', result)
        self.assertIn('create_date', result)
        self.assertIn('updated_date', result)
        self.assertIn('status', result)

        self.assertEqual(result['is_liked'], False)
        self.assertEqual(result['publish_by'], 'nick')
        self.assertEqual(result['person_likes'], ['test@gmail.com'])
        self.assertEqual(result['title'], 'Happy Moment 2')
        self.assertEqual(result['file'], 'http://testserver/media/test_image_2.jpg')
        self.assertEqual(result['total_likes'], 0)
        self.assertEqual(result['status'], True)
    # End List

    # Start Happy Like
    def test_happy_like_authenticated(self):
        url = reverse('happy-like')
        data = {"id": self.happy_moment_2.id}

        initial_likes = self.happy_moment_2.person_likes.count()

        response = self.client.post(url, data, format="json")
        self.happy_moment_2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(self.happy_moment_2.person_likes.filter(id=self.teenandparent.id).exists())
        self.assertEqual(self.happy_moment_2.total_likes, 0)

    def test_happy_unlike_authenticated(self):
        url = reverse('happy-like')
        data = {"id": self.happy_moment_1.id}

        if not self.happy_moment_1.person_likes.filter(id=self.teenandparent.id).exists():
            self.client.post(url, data, format="json")
            self.happy_moment_1.refresh_from_db()

        initial_likes = self.happy_moment_1.person_likes.count()

        response = self.client.post(url, data, format="json")
        self.happy_moment_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(self.happy_moment_1.person_likes.filter(id=self.teenandparent.id).exists())
        self.assertEqual(self.happy_moment_1.total_likes, initial_likes - 1)

    def test_happy_like_unauthenticated(self):
        url = reverse('happy-like')
        self.client.logout()
        data = {"id": self.happy_moment_1.id}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_happy_like_invalid_post_id(self):
        url = reverse('happy-like')
        data = {"id": 9999}  # Non-existent post ID

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("msg", response.data)
    # End Happy Like

    def tearDown(self):
        if os.path.isfile(self.avatar.image.path):
            os.remove(self.avatar.image.path)

        if hasattr(self.valid_file, 'temporary_file_path') and os.path.isfile(self.valid_file.temporary_file_path()):
            os.remove(self.valid_file.temporary_file_path())

        HappyMoments.objects.all().delete()
        TeenagerAndParent.objects.all().delete()
        Avatar.objects.all().delete()
        Accounts.objects.all().delete()
