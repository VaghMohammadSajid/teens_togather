from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.views import APIView
from .serializers import AppointmentSerializer,PaymentSerializer
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Appointment
from Doctor_Module.permission import IsDocUser
from .pagination import AppointmeantPagination
from .models import Appointment
from rest_framework import status, generics
from rest_framework import filters
from Doctor_Module.models import DoctorProfileModel
from Doctor_Module.permission import IsAdminOrDocUser
import logging
from utils.filter_utils import filter_utils
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_date
# Create your views here.



logger = logging.getLogger(__name__)


class AppointmentApi(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description=("![Figma Screenshot](https://adminoneupv1.stackerbee.com/media/cache/bf/6c/bf6c480479daa6c9604f7ffb19b3e683.jpg)\n\n"
        "### Parameters:\n"),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'doctor_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='docto_id'),
                'from_time': openapi.Schema(type=openapi.FORMAT_DATETIME, description='from_time'),
                "to_time":openapi.Schema(type=openapi.FORMAT_DATETIME, description='to_time'),
                }
        ),
        responses={200: 'appointmeant created', 400: 'Bad Request',401:"401_UNAUTHORIZED"}
    )
    def post(self,request):
        data = request.data
        appointment_ser_ob = AppointmentSerializer(data=data,context={'user': request.user,"doctor_id":data['doctor_id']})
        
        if appointment_ser_ob.is_valid():
            appointment_ser_ob.save()
            return  Response({"msg":"appointmeant created"},status=status.HTTP_201_CREATED)
        else:
            return Response({"error":appointment_ser_ob.errors},status=status.HTTP_400_BAD_REQUEST)
        


class PaymentConfirm(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Create a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'appointment': openapi.Schema(type=openapi.TYPE_NUMBER, description='appointmeant_id'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='amount'),
                
                }
        ),
        responses={200: 'paymeant created', 400: 'Bad Request',401:"401_UNAUTHORIZED"}
    )
    def post(self,request):
        data = request.data
        serializer_obj = PaymentSerializer(data=data,context={"user":request.user})
        if serializer_obj.is_valid():
            serializer_obj.save()
            return Response({"msg":"paymeant created"},status=status.HTTP_201_CREATED)
        return Response({"error":serializer_obj.errors},status=status.HTTP_400_BAD_REQUEST)
    

    

    
    
class AppointmeantList(generics.ListAPIView):
    
    
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAdminOrDocUser]
    pagination_class = AppointmeantPagination

    
    @swagger_auto_schema(
        operation_description="Retrieve a list of appointments with optional filters.",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search query to filter by doctor details.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'from_date', openapi.IN_QUERY,
                description="Filter appointments from this date (YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'to_date', openapi.IN_QUERY,
                description="Filter appointments to this date (YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
      
            openapi.Parameter(
                'gender', openapi.IN_QUERY,
                description="Filter by user's gender (Male/Female/Other).",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'payment_status', openapi.IN_QUERY,
                description="Filter by payment status (Paid/Unpaid).",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'created_date', openapi.IN_QUERY,
                description="Filter by created date (YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
             openapi.Parameter(
            'doctorname', openapi.IN_QUERY,
            description="Filter by doctor's first name.",
            type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
            'nickname', openapi.IN_QUERY,
            description="Filter by nickname's ",
            type=openapi.TYPE_STRING
            ),

        
        ],
        responses={
            200: openapi.Response(description="Appointment List Retrieved Successfully"),
            404: openapi.Response(description="No Appointments Found")
        }
    )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        

        return response
    
    def get_queryset(self):
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        #if you need to add more filters you can add here like key value pairs,
        list_filter = {"gender":"user__gender","from_date":"from_time","to_date":"to_time__lte","payment_status" :"payment_status","created_date": "created_date__gte","doctorname":"doctor__accounts__first_name__icontains","price":"doctor__amount","nickname":"user__nick_name__icontains"}
        queryset = super().get_queryset()

        if  created_date_last := self.request.query_params.get("created_date", None):
            input_date = parse_date(created_date_last)
            last_date = input_date + timedelta(days=1)
            queryset = queryset.filter(created_date__lte=last_date)
            
        
        #this is a filter function avilabile in utils. In that function there is filter working that function will be create the quray
        queryset = filter_utils(queryset=queryset,filter_dict=list_filter,obj=self)

        try:
            doc_object = DoctorProfileModel.objects.get(account=self.request.user)
            queryset = queryset.filter(doctor=doc_object)
        except:
            pass

       
        

        return queryset
    
        
class AppointmeantListByDoc(APIView):
    permission_classes= [ IsDocUser]
    @swagger_auto_schema(
        operation_description="Create a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                
                'from': openapi.Schema(type=openapi.FORMAT_DATETIME, description='from_time'),
                "to":openapi.Schema(type=openapi.FORMAT_DATETIME, description='to_time'),
              

                }
        ),
        responses={200: 'appointmeant created', 400: 'Bad Request',401:"401_UNAUTHORIZED"}
    )
    
    def post(self,request):
        data = request.data
        if not (data.get("from") == None) or not (data.get("to") == None):
            appointmeant_query = Appointment.objects.filter(from_time__gte=data.get("from"),to_time__gte=data.get("to"),doctor__account__id=request.user.id)
            appoint_ser = AppointmentSerializer(appointmeant_query,many=True,)
            return Response({"data":appoint_ser.data},status=status.HTTP_200_OK)
        return Response({"error":"please enter a valid date"},status=status.HTTP_400_BAD_REQUEST)