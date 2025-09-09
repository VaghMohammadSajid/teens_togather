
from drf_yasg import openapi


signup_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
        'msg': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
    },
)

signup_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'user_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of user'),
        'concentrate': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='List of concentrates'),
        'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Date of birth'),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email address'),
        'gender': openapi.Schema(type=openapi.TYPE_STRING, description='Gender'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        'mobile_key': openapi.Schema(type=openapi.TYPE_STRING, description='Mobile OTP key'),
        'email_key': openapi.Schema(type=openapi.TYPE_STRING, description='Email OTP key'),
        'nick_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nick name'),
        'avatar_id': openapi.Schema(type=openapi.TYPE_STRING, description='id of the avatar'),
    },
    required=['email', 'password', 'mobile_key', 'email_key','user_type','date_of_birth','gender','nick_name','avatar_id'],  # Specify required fields
)

send_otp_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number to send OTP')
    },
    required=['number']
)


send_otp_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'msg': openapi.Schema(type=openapi.TYPE_STRING, description='Response message indicating OTP status')
    }
)

otp_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'msg': openapi.Schema(type=openapi.TYPE_STRING, description='Response message'),
        'otp_key': openapi.Schema(type=openapi.TYPE_STRING, description='Unique key associated with verified OTP', required=['msg']),
    }
)


verify_mobile_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number to verify OTP for'),
        'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP sent to the phone number'),
    },
    required=['number', 'otp']
)

send_email_otp_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email to send OTP to'),
    },
    required=['email']
)

verify_email_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email to verify OTP for'),
        'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP sent to the email'),
    },
    required=['email', 'otp']
)
