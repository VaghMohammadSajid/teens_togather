from .models import Appointment,Payment
from rest_framework import serializers
from Doctor_Module.models import DoctorProfileModel
import logging
from django.utils import timezone

from Doctor_Module.models import AvailableTime
from Acoounts.models import TeenagerAndParent
from Acoounts.serializer import ConcentrateSerializer

logger = logging.getLogger(__name__)


class AppointmentSerializer(serializers.ModelSerializer):

    nickname = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    concentrated_on = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()


    
    
    def validate(self, attrs):
        try:
            attrs["doctor"] = DoctorProfileModel.objects.get(id=self.context['doctor_id'])
        except DoctorProfileModel.DoesNotExist:
            raise serializers.ValidationError("enter a valid doc id")
        except Exception as e:
            logger.error("error in validating doc for appointmeant", exc_info=True)
            raise serializers.ValidationError("Doc issue found")
        try:
            attrs['user'] = TeenagerAndParent.objects.get(account=self.context['user'])
        except:
            logger.error("error in validating doc for appointmeant", exc_info=True)
            raise serializers.ValidationError("Doc issue found")
        if attrs['from_time'] >= attrs['to_time']:
        
            raise serializers.ValidationError("from_time must be earlier than to_time.")
        if attrs['from_time'] < timezone.now():
            raise serializers.ValidationError("this time has already behind")
        from_datetime_obj =attrs['from_time']
        to_datetime_obj = attrs['to_time']


        time_difference = to_datetime_obj - from_datetime_obj


        is_one_hour_exactly_on_hour = (
            time_difference == timezone.timedelta(hours=1) and
            from_datetime_obj.minute == 0 and
            to_datetime_obj.minute == 0
        )
        if not is_one_hour_exactly_on_hour:
            raise serializers.ValidationError("time must be exactly in hour")
        
        if Appointment.objects.filter(doctor=attrs["doctor"],from_time=attrs["from_time"],to_time=attrs["to_time"]).exists():
            raise serializers.ValidationError("Appointment Alredy Booked")
        
        available_q = AvailableTime.objects.filter(from_time=attrs["from_time"],to_time=attrs["to_time"],doctor=attrs["doctor"])
        if not available_q.exists():
            raise serializers.ValidationError("doctor not available at this time") 
        else:
            available_q.first().status = False
            available_q.first().save()
        return  attrs
    
    
    def create(self, validated_data):
        try:
            validated_data["doctor"] = DoctorProfileModel.objects.get(id=self.context['doctor_id'])
        except DoctorProfileModel.DoesNotExist:
            logger.error("error in validating doc for appointmeant", exc_info=True)
            raise serializers.ValidationError("enter a valid doc id")
        try:
            validated_data['user'] = TeenagerAndParent.objects.get(account=self.context['user'])
        except Exception as e:

            logger.error("error in create appointmeant ser",exc_info=True)
            raise serializers.ValidationError("is while creating obj")
       
    
        
        return super().create(validated_data)
        
    class Meta:
        fields = '__all__'
        model = Appointment
        extra_kwargs = {
            'doctor': {'required': False} ,
            'user': {'required': False}
        }
    def get_nickname(self,obj):
        return f"{obj.user.nick_name}"
    
    def get_doctor_name(self,obj):
        return  f"{obj.doctor.accounts.first_name} {obj.doctor.accounts.last_name}"
    def get_created_date(self,obj):
        return obj.created_date

    def get_concentrated_on(self,obj):
        return ConcentrateSerializer(obj.user.concentrate_on.all(),many=True).data
    def get_gender(self,obj):
        return f"{obj.user.gender}"
    def get_date_of_birth(self,obj):
        return f"{obj.user.date_of_birth}"
    def get_price(self,obj):
        return f"{obj.doctor.amount}"



class PaymentSerializer(serializers.Serializer):
    class Meta:
        fields = "__all__"
        model = Payment

    def validate(self, attrs):
        if attrs["appointment"] == None:
            raise serializers.ValidationError("need a appointmenat id")
        if attrs["amount"] == 0 or attrs["amount"] == "0":
            serializers.ValidationError("need an amount greater than zero")
        try:
            attrs["appointment"] = Appointment.objects.get(id=1)
        except Appointment.DoesNotExist:
            serializers.ValidationError("enter a valid appointmeant id")
        except Exception as e:
            logger.error("issue in payment serializer",exc_info=True)

        return attrs
    
    def create(self, validated_data):
        appointmeant = validated_data['appointment']
        appointmeant.payment_status = "CONFIRM"
        appointmeant.save()
        try:
            paymeant_obj = Payment.objects.get(appointmeant=appointmeant)
            paymeant_obj.amount = paymeant_obj.amount + int(validated_data["amount"])
            paymeant_obj.save()
        except:
            try:
                Payment.objects.create(appointmeant=appointmeant,amount=int(validated_data["amount"]))
            except:
                logger.error("issue while creating payment",exc_info=True)
                raise serializers.as_serializer_error("error in payment creation")
        return True