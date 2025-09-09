from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from Acoounts.models import Accounts, TeenagerAndParent, Avatar
from Doctor_Module.models import DoctorProfileModel, AvailableTime, ReviewAndRating, DoctorProfileModelEdit
from faker import Faker
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from unittest.mock import patch, MagicMock
from Voice_of_the_day.tests import generate_test_image
import os

fake = Faker()


class DoctorProfileApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Accounts.objects.create_superuser(
            email="admin@gmail.com",
            password="admin",
            first_name="Admin",
            last_name="Sharma",
            username="admin@gmail.com",
            phone_number="+91 8888888888",
            designation="ADMIN",
        )

        self.user = Accounts.objects.create_user(
            username="test@gmail.com",
            email="test@gmail.com",
            phone_number="+91 4242424242",
            designation="DOC",
            password="Test@123",
            first_name="Test",
            last_name="Doctor",
        )
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()

        self.doctor_profile = DoctorProfileModel.objects.create(
            accounts=self.user,
            doctor_type="Therapist",
            amount="400",
            experience="11",
            about="nice doctor",
        )

        naive_from_time = datetime.strptime('2025-01-04 10:30', '%Y-%m-%d %H:%M')
        naive_to_time = datetime.strptime('2025-01-04 11:30', '%Y-%m-%d %H:%M')

        from_time = timezone.make_aware(naive_from_time)
        to_time = timezone.make_aware(naive_to_time)

        self.availableTime = AvailableTime.objects.create(
            from_time=from_time,
            to_time=to_time,
            doctor=self.doctor_profile,
            status=True,
        )

        self.avatar = Avatar.objects.create(image="Test.jpg")

        self.teenandparent = TeenagerAndParent.objects.create(
            account=self.user,
            avatar=self.avatar,
            nick_name="nick",
            date_of_birth=fake.date(),
            gender=fake.random.choice(['Male', 'Female']),
        )

        self.doctor_profile_model_edit = DoctorProfileModelEdit.objects.create(
            accounts=self.doctor_profile,
        )

        self.client.force_authenticate(user=self.user)

    def test_create_doctor_profile(self):
        url = reverse('doc-create')

        profile_pic = generate_test_image()

        data = {
            "email": "Test@gmail.com",
            "phone_number": "9999999990",
            "first_name": "Test",
            "last_name": "Doctor",
            "doctor_type": "Therapist",
            "amount": "300",
            "experience": "10",
            "about": "Top doctor in the city",
            "profile_pic": profile_pic
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DoctorProfileModel.objects.count(), 2)

        doc_instance = DoctorProfileModel.objects.last()
        self.assertIsNotNone(doc_instance.profile_pic)
        self.assertTrue(os.path.isfile(doc_instance.profile_pic.path))

    def test_update_doctor_profile(self):
        url = reverse('doc-update', kwargs={'pk': self.doctor_profile.pk})
        data = {
            "accounts": self.user,
            "doctor_type": "Surgeon",
            "amount": "500",
            "experience": "20",
            "about": "Expert in various surgeries",
            "profile_pic": generate_test_image()
        }
        response = self.client.put(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor_profile.refresh_from_db()
        self.assertEqual(self.doctor_profile.doctor_type, "Surgeon")

    def test_list_doctor_profiles(self):
        url = reverse('doc-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        self.assertEqual(response.data['count'], DoctorProfileModel.objects.count())
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        results = response.data['results']
        self.assertEqual(len(results), 1)

        result = results[0]
        self.assertIn('id', result)
        self.assertIn('accounts', result)
        self.assertIn('doctor_type', result)
        self.assertIn('amount', result)
        self.assertIn('experience', result)
        self.assertIn('about', result)
        self.assertIn('average_rating', result)
        self.assertIn('created_at', result)
        self.assertIn('profile_pic', result)

        accounts = result['accounts']
        self.assertIn('email', accounts)
        self.assertIn('phone_number', accounts)
        self.assertIn('designation', accounts)
        self.assertIn('first_name', accounts)
        self.assertIn('last_name', accounts)

        self.assertEqual(result['accounts']['email'], 'test@gmail.com')
        self.assertEqual(result['accounts']['phone_number'], '+91 4242424242')
        self.assertEqual(result['accounts']['designation'], 'DOC')
        self.assertEqual(result['accounts']['first_name'], 'Test')
        self.assertEqual(result['accounts']['last_name'], 'Doctor')
        self.assertEqual(result['doctor_type'], 'Therapist')
        self.assertEqual(result['amount'], '400')
        self.assertEqual(result['experience'], '11')
        self.assertEqual(result['about'], 'nice doctor')
        self.assertEqual(result['average_rating'], 0.0)
        self.assertIsNone(result['profile_pic'])

        try:
            datetime.fromisoformat(result['created_at'].replace('Z', '+00:00'))
        except ValueError:
            self.fail("created_at is not in ISO format")

    def test_doctor_profile(self):
        url = reverse('doc-profile', kwargs={'pk': self.doctor_profile.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('id', response.data)
        self.assertIn('accounts', response.data)
        self.assertIn('doctor_type', response.data)
        self.assertIn('amount', response.data)
        self.assertIn('experience', response.data)
        self.assertIn('about', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('profile_pic', response.data)
        self.assertIn('reviews', response.data)
        self.assertIn('available_times', response.data)

        accounts = response.data['accounts']
        self.assertIn('email', accounts)
        self.assertIn('phone_number', accounts)
        self.assertIn('designation', accounts)
        self.assertIn('first_name', accounts)
        self.assertIn('last_name', accounts)

        self.assertEqual(accounts['email'], 'test@gmail.com')
        self.assertEqual(accounts['phone_number'], '+91 4242424242')
        self.assertEqual(accounts['designation'], 'DOC')
        self.assertEqual(accounts['first_name'], 'Test')
        self.assertEqual(accounts['last_name'], 'Doctor')

        self.assertEqual(response.data['doctor_type'], 'Therapist')
        self.assertEqual(response.data['amount'], '400')
        self.assertEqual(response.data['experience'], '11')
        self.assertEqual(response.data['about'], 'nice doctor')
        self.assertEqual(response.data['average_rating'], 0.0)
        self.assertIsNone(response.data['profile_pic'])

        try:
            datetime.fromisoformat(response.data['created_at'].replace('Z', '+00:00'))
        except ValueError:
            self.fail("created_at is not in ISO 8601 format")

        self.assertIsInstance(response.data['reviews'], list)
        self.assertEqual(len(response.data['reviews']), 0)

        available_times = response.data['available_times']
        self.assertIsInstance(available_times, list)
        self.assertEqual(len(available_times), 1)

        available_time = available_times[0]
        self.assertIn('date', available_time)
        self.assertIn('slots', available_time)

        self.assertEqual(available_time['date'], '2025-01-04')
        slots = available_time['slots']
        self.assertIsInstance(slots, list)
        self.assertEqual(len(slots), 1)

        slot = slots[0]
        self.assertIn('from_time', slot)
        self.assertIn('to_time', slot)
        self.assertIn('status', slot)

        self.assertEqual(slot['from_time'], '2025-01-04T10:30:00Z')
        self.assertEqual(slot['to_time'], '2025-01-04T11:30:00Z')
        self.assertEqual(slot['status'], True)

    def test_doctor_profile_admin(self):
        url = reverse('user-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('accounts', response.data)
        self.assertIn('doctor_type', response.data)
        self.assertIn('amount', response.data)
        self.assertIn('experience', response.data)
        self.assertIn('about', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('profile_pic', response.data)
        self.assertIn('reviews', response.data)

        accounts = response.data['accounts']
        self.assertIn('email', accounts)
        self.assertIn('phone_number', accounts)
        self.assertIn('designation', accounts)
        self.assertIn('first_name', accounts)
        self.assertIn('last_name', accounts)

        self.assertEqual(accounts['email'], 'test@gmail.com')
        self.assertEqual(accounts['phone_number'], '+91 4242424242')
        self.assertEqual(accounts['designation'], 'DOC')
        self.assertEqual(accounts['first_name'], 'Test')
        self.assertEqual(accounts['last_name'], 'Doctor')

        self.assertEqual(response.data['doctor_type'], 'Therapist')
        self.assertEqual(response.data['amount'], '400')
        self.assertEqual(response.data['experience'], '11')
        self.assertEqual(response.data['about'], 'nice doctor')
        self.assertEqual(response.data['average_rating'], 0.0)
        self.assertIsNone(response.data['profile_pic'])

        try:
            datetime.fromisoformat(response.data['created_at'].replace('Z', '+00:00'))
        except ValueError:
            self.fail("created_at is not in ISO 8601 format")

        self.assertIsInstance(response.data['reviews'], list)
        self.assertEqual(len(response.data['reviews']), 0)
    # Start 'add-review'

    def test_delete_doctor_profile(self):
        url = reverse('doc-available-delete', kwargs={'id': self.availableTime.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AvailableTime.objects.count(), 0)

    def test_create_review_authenticated_user(self):
        url = reverse('add-review')
        valid_data = {
            'user_id': self.teenandparent.id,
            'doctor_id': self.doctor_profile.id,
            'review': 'Excellent Doctor',
            'rating': 5,
        }

        response = self.client.post(url, valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReviewAndRating.objects.count(), 1)
        review = ReviewAndRating.objects.first()
        self.assertEqual(review.rating, valid_data['rating'])
        self.assertEqual(review.review, valid_data['review'])

    def test_create_review_invalid_data(self):
        url = reverse('add-review')
        invalid_data = {
            'user_id': self.teenandparent.id,
            'doctor_id': self.doctor_profile.id,
            'review': '',
            'rating': '6',
        }
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ReviewAndRating.objects.count(), 0)

    def test_create_review_unauthenticated_user(self):
        self.client.logout()
        url = reverse('add-review')
        valid_data = {
            'user': self.teenandparent,
            'doctor': self.doctor_profile,
            'review': '',
            'rating': '5',
        }
        response = self.client.post(url, valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ReviewAndRating.objects.count(), 0)
    # End 'add-review'

    # Start Available Time
    def test_available_time_create(self):
        AvailableTime.objects.filter(doctor=self.doctor_profile).delete()

        url = reverse('add-availabletime')
        naive_from_time = datetime.strptime('2025-01-04 10:30', '%Y-%m-%d %H:%M')
        naive_to_time = datetime.strptime('2025-01-04 11:30', '%Y-%m-%d %H:%M')

        from_time = timezone.make_aware(naive_from_time)
        to_time = timezone.make_aware(naive_to_time)

        data = {
            'time_slots': [
                {
                    'from_time': from_time.isoformat(),
                    'to_time': to_time.isoformat()
                }
            ]
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('msg', response.data)
        self.assertEqual(response.data['msg'], "available time updated")
        self.assertEqual(AvailableTime.objects.count(), 1)
    # End Available Time

    # Start doc-available-list-admin
    def test_doc_available_list_admin(self):
        AvailableTime.objects.filter(doctor=self.doctor_profile).delete()
        url = reverse('doc-available-list-admin')

        naive_from_time = datetime.strptime('2025-01-04 10:30', '%Y-%m-%d %H:%M')
        naive_to_time = datetime.strptime('2025-01-04 11:30', '%Y-%m-%d %H:%M')
        from_time = timezone.make_aware(naive_from_time)
        to_time = timezone.make_aware(naive_to_time)

        available_create_2 = AvailableTime.objects.create(
            from_time=from_time,
            to_time=to_time,
            doctor=self.doctor_profile,
            status=True,
            created_at=timezone.now() - timedelta(days=1)
        )
        response = self.client.get(url, {'created_at': '2025-09-22'}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        self.assertEqual(response.data['count'], AvailableTime.objects.count())
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        self.assertEqual(len(response.data['results']), 1)

        results = response.data['results']
        self.assertEqual(len(results), 1)

        result = results[0]
        self.assertIn('from_time', result)
        self.assertIn('to_time', result)
        self.assertIn('status', result)
        self.assertIn('created_at', result)

        self.assertEqual(result['from_time'], from_time.isoformat().replace('+00:00', 'Z'))
        self.assertEqual(result['to_time'], to_time.isoformat().replace('+00:00', 'Z'))
        self.assertEqual(result['created_at'], available_create_2.created_at.isoformat().replace('+00:00', 'Z'))

        self.assertEqual(result['status'], True)

    def test_doc_available_delete_admin(self):
        url = reverse('doc-available-delete', kwargs={'id': self.availableTime.id})
        response = self.client.delete(url)

        self.assertTrue(response.data['success'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(AvailableTime.objects.filter(id=self.availableTime.id).exists())
    # End doc-available-list-admin

    # Start process_doctor_profile_edit
    def test_process_doctor_profile_edit_for_not_pending(self):
        self.doctor_profile_model_edit_1 = DoctorProfileModelEdit.objects.create(
            accounts=self.doctor_profile,
            rejection_reason='retirement',
            status='verified',
        )
        url = reverse('process_doctor_profile_edit', kwargs={'edit_id': self.doctor_profile_model_edit_1.pk})

        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Only pending requests can be processed.')

    def test_process_doctor_profile_edit_for_action_required(self):
        url = reverse('process_doctor_profile_edit', kwargs={'edit_id': self.doctor_profile_model_edit.pk})

        response = self.client.post(url, {'action': None}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Action is required (accept or reject).')

        response = self.client.post(url, {'action': 'abc'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid action. It must be "accept" or "reject".')

    def test_process_doctor_profile_edit_for_accepts(self):
        url = reverse('process_doctor_profile_edit', kwargs={'edit_id': self.doctor_profile_model_edit.pk})

        self.doctor_profile_model_edit.rejection_reason = None

        response = self.client.post(url, {'action': 'accept'}, format='json')

        self.doctor_profile_model_edit.refresh_from_db()
        self.doctor_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Profile edit accepted successfully.')
        self.assertEqual(self.doctor_profile_model_edit.status, 'verified')
        self.assertIsNone(self.doctor_profile_model_edit.rejection_reason)

        for field_edit in self.doctor_profile_model_edit.field_edits.all():
            self.assertEqual(getattr(self.doctor_profile, field_edit.field_name), field_edit.field_value)

    def test_process_doctor_profile_edit_for_not_found_rejection_reason(self):
        url = reverse('process_doctor_profile_edit', kwargs={'edit_id': self.doctor_profile_model_edit.pk})

        response = self.client.post(url, {'action': 'reject', 'rejection_reason': None}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Rejection reason is required.')

    def test_process_doctor_profile_edit_for_rejects(self):
        url = reverse('process_doctor_profile_edit', kwargs={'edit_id': self.doctor_profile_model_edit.pk})

        self.doctor_profile_model_edit.rejection_reason = None
        self.doctor_profile_model_edit.rejection_reason = None

        response = self.client.post(url, {'action': 'reject', 'rejection_reason': 'he is not a capable'},
                                    format='json')

        self.doctor_profile_model_edit.refresh_from_db()
        self.doctor_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Profile edit rejected successfully.')
        self.assertEqual(self.doctor_profile_model_edit.status, 'rejected')
        self.assertEqual(self.doctor_profile_model_edit.rejection_reason, 'he is not a capable')

        for field_edit in self.doctor_profile_model_edit.field_edits.all():
            self.assertEqual(getattr(self.doctor_profile, field_edit.field_name), field_edit.field_value)
    # End process_doctor_profile_edit

    # Start doctor-profile-edit-list
    def test_doctor_profile_edit_list(self):
        url = reverse('doctor-profile-edit-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('doctor_profile_edits', response.data)

        doctor_profile_edits = response.data['doctor_profile_edits']
        self.assertIsInstance(doctor_profile_edits, list)
        self.assertGreater(len(doctor_profile_edits), 0)

        first_edit = doctor_profile_edits[0]
        self.assertIn('id', first_edit)
        self.assertEqual(first_edit['id'], 12)
        self.assertIn('accounts_username', first_edit)
        self.assertEqual(first_edit['accounts_username'], 'test@gmail.com')
        self.assertIn('status', first_edit)
        self.assertEqual(first_edit['status'], 'pending')
        self.assertIn('rejection_reason', first_edit)
        self.assertIsNone(first_edit['rejection_reason'])
        self.assertIn('created_at', first_edit)
        self.assertIn('field_edits', first_edit)
        self.assertIsInstance(first_edit['field_edits'], list)
    # End doctor-profile-edit-list

    # Start doctor-profile-edit-detail
    def test_doctor_profile_edit_detail(self):
        url = reverse('doctor-profile-edit-detail')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('doctor_profile_edits', response.data)
        doctor_profile_edits = response.data['doctor_profile_edits']

        self.assertIsInstance(doctor_profile_edits, list)
        self.assertGreater(len(doctor_profile_edits), 0)

        first_doctor_profile_edits = doctor_profile_edits[0]
        self.assertIn('id', first_doctor_profile_edits)
        self.assertEqual(first_doctor_profile_edits['id'], 11)

        self.assertIn('accounts_username', first_doctor_profile_edits)
        self.assertEqual(first_doctor_profile_edits['accounts_username'], 'test@gmail.com')

        self.assertIn('status', first_doctor_profile_edits)
        self.assertEqual(first_doctor_profile_edits['status'], 'pending')

        self.assertIn('rejection_reason', first_doctor_profile_edits)
        self.assertIsNone(first_doctor_profile_edits['rejection_reason'])

        self.assertIn('created_at', first_doctor_profile_edits)

        self.assertIn('field_edits', first_doctor_profile_edits)
        self.assertIsInstance(first_doctor_profile_edits['field_edits'], list)
    # End doctor-profile-edit-detail

    @patch('Doctor_Module.models.DoctorProfileModel.objects.get')
    def test_does_not_exist_for_admin_user(self, mock_get):
        mock_get.side_effect = DoctorProfileModel.DoesNotExist
        self.client.force_authenticate(user=self.admin)

        url = reverse('user-detail')
        response = self.client.get(url)

        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], self.admin.email)

    @patch('Doctor_Module.models.DoctorProfileModel.objects.get')
    def test_does_not_exist_for_regular_user(self, mock_get):
        mock_get.side_effect = DoctorProfileModel.DoesNotExist

        url = reverse('user-detail')
        profile_pic = generate_test_image()
        data = {
            "email": "Test2@gmail.com",
            "phone_number": "9999999930",
            "first_name": "Test",
            "last_name": "Doctor",
            "doctor_type": "Therapist",
            "amount": "300",
            "experience": "10",
            "about": "Top doctor in the city",
            "profile_pic": profile_pic
        }
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], "You do not have a profile.")

        url = reverse('doctor_profile_edit')
        data_for_doctor_profile_edit = {
            'email': 'testfordoctorprofileedit@gmail.com',
            'phone_number': '1425368594',
            'first_name': 'testfordoctorprofileedit',
            'last_name': 'Sharma',
            'doctor_type':'therapist',
            'amount': 450.00,
            'experience':10,
            'about': 'this is a therapist doc'
        }
        response = self.client.post(url, data_for_doctor_profile_edit)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Doctor profile not found.")

        url = reverse('doctor-profile-edit-detail')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Doctor profile not found.")

    @patch('django.db.transaction.atomic')
    def test_exception_handling_in_post(self, mock_atomic):
        mock_atomic.side_effect = Exception("Simulated exception")

        url = reverse('process_doctor_profile_edit', kwargs={'edit_id': self.doctor_profile_model_edit.pk})
        response = self.client.post(url, {'action': 'accept'})

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], 'An error occurred while processing the request.')
        self.assertIn('details', response.data)
        self.assertEqual(response.data['details'], 'Simulated exception')

        url = reverse('doctor_profile_edit')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Simulated exception')

        profile_pic = generate_test_image()
        url = reverse('doc-create')
        data={
            "email": "Test1@gmail.com",
            "phone_number": "9999999920",
            "first_name": "Test",
            "last_name": "Doctor",
            "doctor_type": "Therapist",
            "amount": "300",
            "experience": "10",
            "about": "Top doctor in the city",
            "profile_pic": profile_pic
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Unexpected Error: Simulated exception')

    def tearDown(self):
        if os.path.isfile(self.avatar.image.path):
            os.remove(self.avatar.image.path)

        DoctorProfileModelEdit.objects.all().delete()
        ReviewAndRating.objects.all().delete()
        AvailableTime.objects.all().delete()
        DoctorProfileModel.objects.all().delete()
        TeenagerAndParent.objects.all().delete()
        Accounts.objects.all().delete()
