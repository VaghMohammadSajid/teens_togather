from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from Acoounts.models import Accounts, Avatar
from appointment.models import Appointment, TeenagerAndParent, Payment
from Doctor_Module.models import DoctorProfileModel, AvailableTime, ReviewAndRating
from django.utils import timezone
from faker import Faker
from Voice_of_the_day.tests import generate_test_image
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
import logging
logger = logging.getLogger(__name__)

fake = Faker()


# class AppointmentApiTestCase(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#
#         self.admin = Accounts.objects.create_superuser(
#             email="admin@gmail.com",
#             password="admin",
#             first_name="Admin",
#             last_name="Sharma",
#             username="admin@gmail.com",
#             phone_number="+91 8888888888",
#             designation="ADMIN",
#         )
#
#         self.client.force_authenticate(self.admin)
#
#         self.teen = Accounts.objects.create_user(
#             username="teens@gmail.com",
#             email="teens@gmail.com",
#             phone_number="+91 4242424242",
#             designation="TEENS",
#             password="teens@123",
#             first_name="Teen",
#             last_name="Test",
#         )
#         self.teen.is_active = True
#         self.teen.is_admin = True
#         self.teen.save()
#
#         self.teen_token = RefreshToken.for_user(self.teen)
#
#         self.avatar = Avatar.objects.create(image="Test.jpg")
#
#         self.teenandparent = TeenagerAndParent.objects.create(
#             account=self.teen,
#             avatar=self.avatar,
#             nick_name="nick",
#             date_of_birth=fake.date(),
#             gender=fake.random.choice(['Male', 'Female']),
#         )
#
#         self.doc_user = Accounts.objects.create_user(
#             email="doc@gmail.com",
#             password="doc",
#             first_name="Doc",
#             last_name="Sharma",
#             username="doc@gmail.com",
#             phone_number="+91 7777777777",
#             designation="DOC",
#         )
#
#         self.doc_user_token = RefreshToken.for_user(self.doc_user)
#
#         self.doctor = DoctorProfileModel.objects.create(
#             accounts=self.doc_user,
#             doctor_type="General",
#             amount=100,
#             experience=10,
#             about="Experienced doctor",
#             profile_pic=generate_test_image()
#         )
#         self.client.logout()
#         self.client.force_authenticate(user=self.doc_user, token=self.doc_user_token.access_token)
#
#         future_from_time = (timezone.now() + timezone.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
#         future_to_time = future_from_time + timezone.timedelta(hours=1)
#
#         from_time = future_from_time.isoformat().replace("+00:00", "")
#         to_time = future_to_time.isoformat().replace("+00:00", "")
#
#         self.available_time = AvailableTime.objects.create(
#             doctor=self.doctor,
#             from_time=from_time,
#             to_time=to_time,
#             status=True
#         )
#
#         logger.debug(
#             f"self.available_time : {self.available_time.doctor, self.available_time.from_time, self.available_time.to_time}")
#
#         self.valid_payload = {
#             "doctor_id": self.doctor.id,
#             "from_time": self.available_time.from_time,
#             "to_time": self.available_time.to_time,
#         }
#
#         self.invalid_payload = {
#             "doctor_id": 999,
#             "from_time": "2025-01-19T16:00:00",
#             "to_time": "2025-01-19T15:00:00"
#         }
#
#         self.client.logout()
#         self.client.force_authenticate(user=self.teen, token=self.teen_token)
#
#     def create_appointment(self, payload):
#         return self.client.post(reverse('appointment-create'), data=payload, format="json")
#
#     def test_create_appointment_success(self):
#         logger.debug("start a test_create_appointment_success")
#
#         logger.debug(f"Doctor id: {self.doctor.id}")
#         logger.debug(f"available from time: {self.available_time.from_time}")
#         logger.debug(f"available to time: {self.available_time.to_time}")
#
#         response = self.create_appointment(self.valid_payload)
#         logger.debug(f"test_create_appointment_success data is: {response.data}")
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data["msg"], "appointmeant created")
#
#         self.assertTrue(Appointment.objects.filter(doctor=self.doctor, user=self.teenandparent, to_time=self.valid_payload['to_time']))
#         appointment = Appointment.objects.get()
#         self.assertEqual(appointment.doctor, self.doctor)
#         self.assertEqual(appointment.user.account, self.teen)
#
#         logger.debug("End test_create_appointment_success")
#
#     def test_create_appointment_invalid_doctor(self):
#         logger.debug("start a test_create_appointment_invalid_doctor")
#         response = self.create_appointment(self.invalid_payload)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
#         self.assertIn("enter a valid doc id", response.data["error"]["non_field_errors"])
#
#         logger.debug("End a test_create_appointment_invalid_doctor")
#
#     def test_create_appointment_invalid_time_range(self):
#         logger.debug("start a test_create_appointment_invalid_time_range")
#
#         response = self.create_appointment({
#             "doctor_id": self.doctor.id,
#             "from_time": "2025-01-19T16:00:00",
#             "to_time": "2025-01-19T12:00:00"
#         })
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("from_time must be earlier than to_time.", response.data["error"]["non_field_errors"][0])
#
#         logger.debug("End a test_create_appointment_invalid_time_range")
#
#     def test_create_appointment_past_time(self):
#         logger.debug("start a test_create_appointment_past_time")
#
#         past_time = "2025-01-16T16:00:00"
#         data = {
#             "doctor_id": self.doctor.id,
#             "from_time": past_time,
#             "to_time": "2025-01-16T17:00:00",
#         }
#         response = self.create_appointment(data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         error_message = response.data.get("error", {}).get("non_field_errors", [""])[0]
#         self.assertIn("this time has already behind", error_message)
#
#         logger.debug("End a test_create_appointment_past_time")
#
#     def test_create_appointment_already_booked(self):
#         logger.debug("start a test_create_appointment_already_booked")
#
#         self.client.logout()
#         self.client.force_authenticate(user=self.teen)
#
#         appointment = Appointment(
#             doctor=self.doctor,
#             user=self.teenandparent,
#             from_time=self.available_time.from_time,
#             to_time=self.available_time.to_time,
#             payment_status="PENDING"
#         )
#         appointment.save()
#
#         data = {
#             "doctor_id": self.doctor.id,
#             "from_time": self.available_time.from_time,
#             "to_time": self.available_time.to_time
#         }
#
#         response = self.create_appointment(data)
#         logger.debug(f"test_create_appointment_already_booked data is : {response.data}")
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("Appointment Already Booked", response.data["error"]["non_field_errors"][0])
#
#         logger.debug("End a test_create_appointment_already_booked")
#
#     def test_create_appointment_time_exactly_hour(self):
#         logger.debug("Start a test_create_appointment_time_exactly_hour")
#
#         from_time = (timezone.now() + timezone.timedelta(hours=1)).replace(minute=15, second=0, microsecond=0)
#         to_time = from_time + timezone.timedelta(hours=2)
#         data = {
#             "doctor_id": self.doctor.id,
#             "from_time": from_time.isoformat(),
#             "to_time": to_time.isoformat()
#         }
#
#         response = self.create_appointment(data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         error_message = response.data.get("error", {}).get("non_field_errors", [""])[0]
#         self.assertIn("time must be exactly in hour", error_message)
#
#         logger.debug("End a test_create_appointment_time_exactly_hour")
#
#     def test_create_appointment_doctor_not_available(self):
#         logger.debug("Start a test_create_appointment_doctor_not_available")
#
#         future_from_time = (timezone.now() + timezone.timedelta(hours=1)).replace(minute=0)
#         future_to_time = future_from_time + timezone.timedelta(hours=1)
#
#         not_available_from_time = future_from_time.isoformat().replace("+00:00", "")
#         not_available_to_time = future_to_time.isoformat().replace("+00:00", "")
#
#         data = {
#             "doctor_id": self.doctor.id,
#             'from_time': not_available_from_time,
#             'to_time': not_available_to_time
#         }
#         response = self.create_appointment(data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         error_message = response.data.get("error", {}).get("non_field_errors", [""])[0]
#         self.assertIn("doctor not available at this time", error_message)
#
#         logger.debug("End a test_create_appointment_doctor_not_available")
#
#     def test_create_appointment_invalid_time_format(self):
#         logger.debug("Start a test_create_appointment_invalid_time_format")
#
#         data = {
#             "doctor_id": self.doctor.id,
#             'from_time': '2025-01-20T06:00:00',
#             'to_time': '2025-01-20T07:00:00'
#         }
#         response = self.create_appointment(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#
#         logger.debug("End a test_create_appointment_invalid_time_format")
#
#     @patch('appointment.models.appointmeant_delete_task.apply_async')
#     def test_create_appointment_triggers_task(self, mock_task):
#         logger.debug("Start a test_create_appointment_triggers_task")
#         response = self.create_appointment(self.valid_payload)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         mock_task.assert_called_once_with(args=[Appointment.objects.get().id], countdown=60)
#
#         logger.debug("End a test_create_appointment_triggers_task")
#
#     def tearDown(self):
#         Appointment.objects.all().delete()
#         AvailableTime.objects.all().delete()
#         TeenagerAndParent.objects.all().delete()
#         DoctorProfileModel.objects.all().delete()
#         Avatar.objects.all().delete()
#         Accounts.objects.all().delete()


# class AppointmeantListByDoc(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#
#         self.doc_user = Accounts.objects.create_user(
#             email="doc11@gmail.com",
#             password="doc11",
#             first_name="Doc11",
#             last_name="Sharma",
#             username="doc11@gmail.com",
#             phone_number="+91 5247986325",
#             designation="DOC",
#         )
#
#         # Authenticate the doctor user
#         self.client.force_authenticate(user=self.doc_user)
#
#         # Create a doctor profile
#         self.doctor = DoctorProfileModel.objects.create(
#             accounts=self.doc_user,
#             doctor_type="Therapists",
#             amount="400",
#             experience="15",
#             about="Experienced and trusted doctor",
#         )
#
#         # Set available time for the doctor
#         self.available_time = AvailableTime.objects.create(
#             doctor=self.doctor,
#             from_time=timezone.now().replace(minute=0, second=0, microsecond=0) + timezone.timedelta(hours=1),
#             to_time=timezone.now().replace(minute=0, second=0, microsecond=0) + timezone.timedelta(hours=2),
#             status=True,
#         )
#
#     def test_appointment_list_by_doc_success(self):
#         self.client.force_authenticate(user=self.doc_user)
#         url = reverse("appointmeant-doc")
#         data = {
#             "from": self.available_time.from_time.isoformat(),
#             "to": self.available_time.to_time.isoformat(),
#         }
#
#         response = self.client.post(url, data)
#         print("test_appointment_list_by_doc_success response data is :", response.data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data["data"]), 1)
#         self.assertEqual(
#             response.data["data"][0]["from_time"], self.available_time.from_time.isoformat()
#         )
#         self.assertEqual(
#             response.data["data"][0]["to_time"], self.available_time.to_time.isoformat()
#         )
#
#     def test_appointment_list_by_doc_invalid_date(self):
#         """Test that an invalid date range returns a 400 error."""
#         url = reverse("appointmeant-doc")
#         data = {"from": "", "to": ""}
#
#         response = self.client.post(url, data)
#         print("test_appointment_list_by_doc_invalid_date response data is :", response.data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("please enter a valid date", response.data.get("error", ""))
#
#     def test_appointment_list_by_doc_no_appointments(self):
#         url = reverse("appointmeant-doc")
#         data = {
#             "from": (timezone.now() + timezone.timedelta(days=10)).isoformat(),
#             "to": (timezone.now() + timezone.timedelta(days=11)).isoformat(),
#         }
#
#         response = self.client.post(url, data)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data["data"]), 0)
#
#     def tearDown(self):
#         """Clean up test data after each test."""
#         Appointment.objects.all().delete()
#         AvailableTime.objects.all().delete()
#         TeenagerAndParent.objects.all().delete()
#         DoctorProfileModel.objects.all().delete()
#         Accounts.objects.all().delete()


# class PaymentConfirmTestCase(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#
#         self.admin = Accounts.objects.create_superuser(
#             email="admin@gmail.com",
#             password="admin",
#             first_name="Admin",
#             last_name="Sharma",
#             username="admin@gmail.com",
#             phone_number="+91 8888888888",
#             designation="ADMIN",
#         )
#         self.client.force_authenticate(user=self.admin)
#
#         self.user_teens = Accounts.objects.create_user(
#             email="teens@gmail.com",
#             password="teens",
#             first_name="Teen",
#             last_name="Sharma",
#             username="teens@gmail.com",
#             phone_number="+91 5468742596",
#             designation="TEENS",
#         )
#         self.teenager_and_parent = TeenagerAndParent.objects.create(account=self.user_teens)
#
#         self.doc_user = Accounts.objects.create_user(
#             email="doc@gmail.com",
#             password="doc",
#             first_name="Doc",
#             last_name="Sharma",
#             username="doc@gmail.com",
#             phone_number="+91 7777777777",
#             designation="DOC",
#         )
#
#         self.doctor_payment = DoctorProfileModel.objects.create(
#             accounts=self.doc_user,
#             doctor_type="Therapist",
#             experience="11",
#             about="Nice doctor",
#         )
#         self.client.logout()
#         self.client.force_authenticate(user=self.doc_user)
#
#         self.available_time = AvailableTime.objects.create(
#             doctor=self.doctor_payment,
#             from_time="2025-01-20T16:00:00Z",
#             to_time="2025-01-20T17:00:00Z",
#             status=True
#         )
#
#         self.client.logout()
#         self.client.force_authenticate(user=self.user_teens)
#
#         self.appointment = Appointment.objects.create(
#             doctor=self.doctor_payment,
#             user=self.teenager_and_parent,
#             from_time=self.available_time.from_time,
#             to_time=self.available_time.to_time,
#             payment_status="PENDING",
#         )
#
#     def payment_create(self, data):
#         return self.client.post(reverse("paymeant"), data=data, format="json")
#
#     def test_payment_not_appointment_id(self):
#         data = {
#             "appointment": '1000',
#             "amount": 200
#         }
#         print("test_payment_not_appointment_id data is:", data)
#         response = self.payment_create(data)
#         print("test_payment_not_appointment_id response is:", response.data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         error_message = response.data.get("error", {}).get("non_field_errors", [""])[0]
#         self.assertEqual(error_message, "need a appointmenat id")
#
#     def test_appointment_does_not_exist(self):
#         appointment=Appointment.objects.get(id=42)
#         data = {
#             "appointment": appointment.id,
#             "amount": 200
#         }
#         print("test_appointment_does_not_exist data is:", data)
#         response = self.payment_create(data)
#         print("test_appointment_does_not_exist response is:", response.data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         error_message = response.data.get("error", {}).get("non_field_errors", [""])[0]
#         self.assertEqual(error_message, "enter a valid appointmeant id")
#
#     def test_payment_creation_success(self):
#         data = {
#             "appointment": self.appointment.id,
#             "amount": 200
#         }
#         print("test_payment_creation_success data is :", data)
#         response = self.payment_create(data)
#         print("test_payment_creation_success response is :", response.data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data["msg"], "paymeant created")
#         self.appointment.refresh_from_db()
#         self.assertEqual(self.appointment.payment_status, "CONFIRM")
#
#     def test_payment_creation_invalid_appointment(self):
#         data = {
#             "appointment": 10000,
#             "amount": 200
#         }
#         response = self.payment_create(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("appointment", response.data["error"])
#
#     def test_payment_creation_zero_amount(self):
#         data = {
#             "appointment": self.appointment.id,
#             "amount": 0
#         }
#         print("test_payment_creation_zero_amount data is:", data)
#         response = self.payment_create(data)
#         print("test_payment_creation_zero_amount response is:", response.data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         error_message = response.data.get("error", {}).get("non_field_errors", [""])[0]
#         self.assertEqual("need an amount greater than zero", error_message)
#
#     def test_duplicate_payment(self):
#         Payment.objects.create(appointment=self.appointment, amount=200)
#
#         data = {
#             "appointment": self.appointment.id,
#             "amount": 100
#         }
#         response = self.payment_create(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         error_message = response.data.get("error", {}).get("non_field_errors", [""])[0]
#         self.assertIn("appointment", error_message)
#
#         payment = Payment.objects.get(appointment=self.appointment)
#         self.assertEqual(payment.amount, 300)
#
#     def test_payment_creation_unavailable_appointment(self):
#         self.appointment.payment_status = "CONFIRM"
#         self.appointment.save()
#         data = {
#             "appointment": self.appointment.id,
#             "amount": 200
#         }
#         response = self.payment_create(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("appointment", response.data["error"])
#
#     def tearDown(self):
#         Payment.objects.all().delete()
#         Appointment.objects.all().delete()
#         TeenagerAndParent.objects.all().delete()
#         DoctorProfileModel.objects.all().delete()
#         Accounts.objects.all().delete()

