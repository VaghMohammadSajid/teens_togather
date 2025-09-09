from django.urls import reverse
from rest_framework import status
from django.utils.timezone import now
from datetime import timedelta, date
from django.utils import timezone
from Acoounts.models import Accounts, Avatar, StoreOtpForEmail, Concentrate, TeenagerAndParent
from appointment.models import Appointment
from Doctor_Module.models import DoctorProfileModel
from rest_framework.test import APITestCase, APIClient
from faker import Faker
from rest_framework.authtoken.models import Token
from unittest.mock import patch
from django.contrib.auth import get_user_model

faker = Faker()

class ApiTokenTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = Accounts.objects.create_user(username='testuser', password='testpassword', email='testuser@example.com',first_name="pranav",last_name="ps",phone_number="8075769725",designation="TEENS")
        # self.admin_user = Accounts.objects.create_superuser(username='admin', password='adminpassword', email='admin@example.com',first_name="pra",last_name="ps",phone_number="7034431702",designation="ADMIN")

    def test_token_obtain_pair_valid(self):
        url = reverse('token_obtain_pair')
        data = {'email': 'testuser@example.com', 'password': 'testpassword'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_obtain_pair_invalid_credentials(self):
        url = reverse('token_obtain_pair')
        data = {'email': 'testuser@example.com', 'password': 'wrongpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_valid(self):
        url = reverse('token_refresh')
        data = {'refresh': self.client.post(reverse('token_obtain_pair'), {'email': 'testuser@example.com', 'password': 'testpassword'}).data['refresh']}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_refresh_invalid(self):
        url = reverse('token_refresh')
        data = {'refresh': 'invalid_refresh_token'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_verify_valid(self):
        token = self.client.post(reverse('token_obtain_pair'), {'email': 'testuser@example.com', 'password': 'testpassword'}).data['access']
        url = reverse('token_verify')
        data = {'token': token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_verify_invalid(self):
        url = reverse('token_verify')
        data = {'token': 'invalid_token'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_admin_login_success(self):
    #     url = reverse('admin_login')
    #     data = {'username': 'admin', 'password': 'adminpassword'}
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_concentrate_list(self):
    #     url = reverse('concentrate-list')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_concentrate_create(self):
    #     url = reverse('concentrate-create')
    #     data = {'name': 'New Concentrate', 'description': 'Description of concentrate'}
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_concentrate_create_invalid(self):
    #     url = reverse('concentrate-create')
    #     data = {'name': '', 'description': 'Description of concentrate'}  # invalid name
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_concentrate_update(self):
    #     # First create a concentrate to update
    #     create_url = reverse('concentrate-create')
    #     self.client.post(create_url, {'name': 'Concentrate to Update', 'description': 'Update me'})

    #     url = reverse('concentrate-update', kwargs={'pk': 1})  # Assuming ID 1
    #     data = {'name': 'Updated Concentrate', 'description': 'Updated description'}
    #     response = self.client.put(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_concentrate_update_invalid(self):
    #     # First create a concentrate to update
    #     create_url = reverse('concentrate-create')
    #     self.client.post(create_url, {'name': 'Concentrate to Update', 'description': 'Update me'})

    #     url = reverse('concentrate-update', kwargs={'pk': 1})  # Assuming ID 1
    #     data = {'name': '', 'description': 'Updated description'}  # invalid name
    #     response = self.client.put(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_concentrate_delete(self):
    #     # First create a concentrate to delete
    #     create_url = reverse('concentrate-create')
    #     self.client.post(create_url, {'name': 'Concentrate to Delete', 'description': 'Delete me'})

    #     url = reverse('concentrate-delete', kwargs={'pk': 1})  # Assuming ID 1
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # def test_concentrate_delete_not_found(self):
    #     url = reverse('concentrate-delete', kwargs={'pk': 999})  # Non-existing concentrate
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ApiEmailVerTests(APITestCase):

    def test_send_email_otp(self):
        url = reverse('send-email-otp')
        data = {"email":"pranav@gmail.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('msg', response.data)

    def test_verify_email(self):
        url = reverse('send-email-otp')
        data = {"email":"pranav@gmail.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = reverse('verify-email-otp')
        data = {"email":"pranav@gmail.com","otp":"123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('msg', response.data)


class ApiEmailPhoneVerTests(APITestCase):

    def test_send_mobile_otp(self):
        url = reverse('send-mobile-otp')
        data = {"number":"8075769725"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('msg', response.data)

    def test_verify_mobile(self):
        url = reverse('send-mobile-otp')
        data = {"number":"8075769725"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = reverse('verify-mobile-otp')
        data = {"number":"8075769725","otp":"123"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('msg', response.data)


class ApiAuthTests(APITestCase):
    def setUp(self):
        url = reverse('send-mobile-otp')
        data = {"number":"8075769725"}
        response = self.client.post(url, data)

        url = reverse('verify-mobile-otp')
        data = {"number":"8075769725","otp":"123"}
        response = self.client.post(url, data)

        self.mobile_key = response.data.get('otp_key')

        url = reverse('send-email-otp')
        data = {"email":"pranav@gmail.com"}
        response = self.client.post(url, data)

        url = reverse('verify-email-otp')
        data = {"email":"pranav@gmail.com","otp":"123"}
        response = self.client.post(url, data)
        self.email_key = response.data.get("otp_key")

    def test_signup_success(self):
        avatar = Avatar.objects.create(image="Test.jpg")
        url = reverse('signup')
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
            "user_type":"TEENS",
            "concentrate":[],
            "date_of_birth":"2007-05-21",
            "phone_number":"8075769725",
            "gender":"male",
            "email_key":self.email_key,
            "mobile_key":self.mobile_key,
            "avatar_id": avatar.id,

        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_signup_existing_user(self):
        avatar = Avatar.objects.create(image="Test.jpg")
        url = reverse('signup')
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
            "user_type":"TEENS",
            "concentrate":[],
            "date_of_birth":"2007-05-21",
            "phone_number":"8075769725",
            "gender":"male",
            "email_key":self.email_key,
            "mobile_key":self.mobile_key,
            "avatar_id": avatar.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        url = reverse('signup')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'testuser@example.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ApiLoginUserTests(APITestCase):
    def setUp(self):
        self.user = Accounts.objects.create_user(username='testuser', password='testpassword', email='testuser@example.com',first_name="pranav",last_name="ps",phone_number="8075769725",designation="TEENS")

    def test_login_success(self):
        url = reverse('login')
        data = {'email': 'testuser@example.com', 'password': 'testpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {'email': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ConcentrateTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.concentrate = Concentrate.objects.create(
            name=faker.name()
        )

        self.client.force_authenticate(user=self.concentrate)

    def test_create_concentrate(self):
        url = reverse('concentrate-create')

        data = {
            'name': faker.name()
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Concentrate.objects.filter(name=data['name']).count(), 1)

    def test_update_concentrate(self):
        url = reverse('concentrate-update', kwargs={'pk': self.concentrate.pk})

        data = {
            'name': faker.name()
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.concentrate.refresh_from_db()
        self.assertEqual(self.concentrate.name, data['name'])

    def test_list_concentrates(self):
        url = reverse('concentrate-list')
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Concentrate.objects.count())

    def test_delete_concentrate(self):
        url = reverse('concentrate-delete', kwargs={'pk': self.concentrate.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Concentrate.objects.count(), 0)


class DashboardAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = Accounts.objects.create_user(
            email="admin@gmail.com",
            password="admin",
            first_name="Admin",
            last_name="Sharma",
            username="Test@gmail.com",
            phone_number="+91 8888888888",
            designation="ADMIN",
        )
        self.admin.is_staff = True
        self.admin.is_active = True
        self.admin.save()
        self.teens = Accounts.objects.create_user(
            email="teens@gmail.com",
            password="teens",
            first_name="Teen",
            last_name="Sharma",
            username="teens@gmail.com",
            phone_number="+91 6823535353",
            designation="TEENS",
        )
        self.parent = Accounts.objects.create_user(
            email="parent@gmail.com",
            password="parent@gmail.com",
            first_name="Parent",
            last_name="Sharma",
            username="parent@gmail.com",
            phone_number="+91 1245638462",
            designation="PARENTS",
        )
        self.doc_user = Accounts.objects.create_user(
            email="doc@gmail.com",
            password="doc",
            first_name="Doc",
            last_name="Sharma",
            username="doc@gmail.com",
            phone_number="+91 7777777777",
            designation="DOC",
        )

        self.client.force_authenticate(self.admin)

    def test_dashboard_api_with_valid_params(self):
        url = reverse('dashboard')
        response = self.client.get(url, {
            'month': 5,
            'year': 2023,
            'designation': 'TEENS',
            'appointment_month': 7,
            'appointment_year': 2023,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn('total_teens', data)
        self.assertIn('total_parents', data)
        self.assertIn('total_doctors', data)
        self.assertIn('daily_registration_data', data)
        self.assertIn('daily_appointment_data', data)

        self.assertEqual(data['total_teens'], 1)
        self.assertEqual(data['total_parents'], 1)
        self.assertEqual(data['total_doctors'], 1)

        self.assertIsInstance(data['daily_registration_data'], list)
        self.assertIsInstance(data['daily_appointment_data'], list)

    def test_dashboard_api_invalid_month_format(self):
        url = reverse('dashboard')
        response = self.client.get(url, {
            'month': 13.5,
            'year': 3.5,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("Invalid month or year format.", response.json().get("error"))

    def test_dashboard_api_no_params(self):
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data['total_teens'], 1)
        self.assertEqual(data['total_parents'], 1)
        self.assertEqual(data['total_doctors'], 1)

    def test_dashboard_api_with_no_data(self):
        url = reverse('dashboard')
        response = self.client.get(url, {
            'month': 12,
            'year': 2025
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data['total_teens'], 1)
        self.assertEqual(data['total_parents'], 1)
        self.assertEqual(data['total_doctors'], 1)
        self.assertEqual(data['daily_registration_data'], [])

    def test_dashboard_api_valid_date_format(self):
        url = reverse('dashboard')
        teen_startdate= "2025-01-01T00:00:00Z",
        teen_enddate = "2025-01-10T23:59:59Z",

        response = self.client.get(url, {
            'teen_startdate': teen_startdate,
            'teen_enddate': teen_enddate,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('total_teens', data)
        self.assertIn('total_parents', data)
        self.assertIn('total_doctors', data)

    def tearDown(self):
        Appointment.objects.all().delete()
        TeenagerAndParent.objects.all().delete()
        DoctorProfileModel.objects.all().delete()
        Accounts.objects.all().delete()


class UserListTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = self.create_admin_user()
        self.normal_user = self.create_normal_user()

        self.url = reverse('user-list')

    def create_admin_user(self):
        self.client = APIClient()

        self.admin = Accounts.objects.create_user(
            email="admin@gmail.com",
            password="admin",
            first_name="Admin",
            last_name="Sharma",
            username="admin@gmail.com",
            phone_number="+91 8888888888",
            designation="ADMIN",
        )
        self.admin.is_staff = True
        self.admin.is_active = True
        self.admin.save()

        return self.admin

    def create_normal_user(self):
        self.teens = Accounts.objects.create_user(
            email="teens@gmail.com",
            password="teens",
            first_name="Teen",
            last_name="Sharma",
            username="teens@gmail.com",
            phone_number="+91 6823535353",
            designation="TEENS",
        )
        self.teens.date_joined = timezone.datetime.now()
        return self.teens

    def test_get_user_list_with_pagination(self):
        self.client.force_authenticate(self.admin_user)
        self.client.login(username="admin@gmail.com", password="admin")

        for i in range(5):
            user = Accounts.objects.create_user(
                email=f"user{i}@gmail.com",
                password="password",
                first_name=f"User{i}",
                last_name="Sharma",
                username=f"user{i}@gmail.com",
                phone_number=f"+91 8888888{i}",
                designation="TEENS",
            )
            self.teens.date_joined = '2025-01-10'
            self.teens.save()
            TeenagerAndParent.objects.create(
                account=user,
                gender="Male",
                nick_name=f"User{i}"
            )

        response = self.client.get(self.url, {"page_size": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertTrue('next' in response.data)

    def test_get_user_list_with_filter_by_email(self):
        self.client.force_authenticate(self.admin_user)
        self.client.login(username="admin", password="admin")

        user1 = Accounts.objects.create_user(
            email="test1@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            username="test1@example.com",
            phone_number="+91 7777777777",
            designation="TEENS",
        )
        user1.date_joined = '2025-01-10'
        user1.save()
        user2 = Accounts.objects.create_user(
            email="test2@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            username="test2@example.com",
            phone_number="+91 7777777770",
            designation="TEENS",
        )
        user2.date_joined = '2025-01-10'
        user2.save()

        TeenagerAndParent.objects.create(account=user1, gender="Male", nick_name="User1")
        TeenagerAndParent.objects.create(account=user2, gender="Male", nick_name="User2")

        response = self.client.get(self.url, {"email": "test1@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['account']['email'], "test1@example.com")

    def test_get_user_list_not_found(self):
        self.client.force_authenticate(self.admin_user)
        self.client.login(username="adminsharma", password="password123")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_get_user_list_with_valid_date_filter(self):
        self.client.force_authenticate(self.admin_user)
        self.client.login(username="teens@gmail.com", password="teens")

        response = self.client.get(self.url, {"created_date": '2025-01-04'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_list_without_permission(self):
        self.client.force_authenticate(self.teens)
        self.client.login(username="user", password="password123")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        TeenagerAndParent.objects.all().delete()
        Accounts.objects.all().delete()


class ChangePasswordApiTest(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = Accounts.objects.create_user(
            email="admin@gmail.com",
            password="admin",
            first_name="Admin",
            last_name="Sharma",
            username="admin@gmail.com",
            phone_number="+91 8888888888",
            designation="ADMIN",
        )
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()

        self.url = reverse('change_password')

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "current_password": "admin",
            "new_password": "newpassword123"
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Password changed successfully")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_change_password_incorrect_current_password(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "current_password": "incorrectpassword",
            "new_password": "newpassword123"
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], "Current password is incorrect")

    @patch('Acoounts.models.Accounts.objects.get')
    def test_change_password_user_does_not_exist(self, mock_get):

        mock_get.side_effect = get_user_model().DoesNotExist
        self.client.force_authenticate(user=self.user)

        data = {
            "current_password": "admin",
            "new_password": "newpassword123"
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "User does not exist")

    def test_change_password_without_authentication(self):
        data = {
            "current_password": "admin",
            "new_password": "newpassword123"
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")


    def tearDown(self):
        Accounts.objects.all().delete()