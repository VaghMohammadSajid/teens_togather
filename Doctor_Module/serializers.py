from rest_framework import serializers
from Doctor_Module.models import DoctorProfileModel,ReviewAndRating,AvailableTime,DoctorProfileModelEdit, DoctorProfileFieldEdit
from Acoounts.models import  Accounts, TeenagerAndParent
from django.db.models import Avg
from django.utils import timezone
from datetime import datetime,timedelta
from collections import defaultdict

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = ['email', 'phone_number', 'designation', 'password',"first_name","last_name"]
        read_only_fields = ['designation',]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['designation'] = "DOC"
        account = Accounts.objects.create(**validated_data)
        return account


class DoctorSerializer(serializers.ModelSerializer):
    accounts = AccountSerializer()

    class Meta:
        model = DoctorProfileModel
        fields = ['id', 'accounts', 'doctor_type', 'amount', 'experience', 'about','average_rating' ,
                  'created_at',"profile_pic"]
        read_only_fields = ['id', 'created_at', 'average_rating' ]

    def create(self, validated_data):
        account_data = validated_data.pop('accounts')
        account_data['designation'] = "DOC"

        account = Accounts.objects.create(**account_data)
        doctor_data = DoctorProfileModel.objects.create(accounts=account,  **validated_data)
        return doctor_data


    def update(self, instance, validated_data):
        account_data = validated_data.pop('accounts', None)

        if account_data:

            account_serializer = AccountSerializer(data=account_data, partial=True)
            if account_serializer.is_valid():
                account_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class BlankSerilaizer(serializers.Serializer):
    pass

class DocProfileSerializer(DoctorSerializer):
    reviews = serializers.SerializerMethodField()
    available_times = serializers.SerializerMethodField()

    class Meta:
        model = DoctorSerializer.Meta.model
        fields = DoctorSerializer.Meta.fields + [ 'reviews','available_times']
        read_only_fields = DoctorSerializer.Meta.read_only_fields 

    def get_reviews(self,obj):
        
        return ReviewSerializer(obj.reviews.all(),many=True).data

    def get_available_times(self, obj):
    
        year = self.context.get('year')
        month = self.context.get('month')

        
        availability = obj.availability.all()
        if year and month:
            availability = availability.filter(
                from_time__year=int(year), 
                from_time__month=int(month)
            )

        grouped_availability = defaultdict(list)
        for slot in availability:
            date = slot.from_time.date()
            grouped_availability[str(date)].append(AvailableTimeSerializer(slot).data)

        # Format the result
        result = []
        for date, slots in grouped_availability.items():
            result.append({
                "date": date,
                "slots": slots
            })
        
        return result 
    
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()


    class Meta:
        model = ReviewAndRating
        fields = ["review","rating","user",'avatar']
    def get_user(self,obj):
        return obj.user.nick_name
    def get_avatar(self,obj):
        if obj.user.avatar:
            return obj.user.avatar.image.url
        return None


class AccountAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = ['email', 'phone_number', 'designation', 'first_name', 'last_name']

class ReviewAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewAndRating
        fields = ['user', 'review', 'rating']    

class DoctorProfileSerializer(serializers.ModelSerializer):
    accounts = AccountSerializer()
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = DoctorProfileModel
        fields = [
            'accounts',
            'doctor_type',
            'amount',
            'experience',
            'about',
            'average_rating',
            'created_at',
            'profile_pic',
            'reviews',
        ]

class AddReviewSerializer(serializers.ModelSerializer):

    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfileModel.objects.all(), write_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=TeenagerAndParent.objects.all(), write_only=True
    )

    class Meta:
        model = ReviewAndRating
        fields = ['user_id', 'doctor_id', 'review', 'rating']

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0 and 5.")

        return value

    def create(self, validated_data):
        user = validated_data.get('user_id')
        doctor = validated_data.get('doctor_id')
        
        
        if ReviewAndRating.objects.filter(user=user, doctor=doctor).exists():
            raise serializers.ValidationError("You have already reviewed this doctor.")

        review = ReviewAndRating.objects.create(
            user=user,
            doctor=doctor,
            review=validated_data.get('review'),
            rating=validated_data.get('rating')
        )
        
        
        doctor_reviews = ReviewAndRating.objects.filter(doctor=doctor)
        average_rating = doctor_reviews.aggregate(
            Avg('rating')
        )['rating__avg']
        doctor.average_rating = average_rating
        doctor.save()
        
        return review

class TimeSlotSerializer(serializers.Serializer):
    from_time = serializers.DateTimeField()
    to_time = serializers.DateTimeField()

class AddAvailableTimeSerializer(serializers.Serializer):  # Change from ModelSerializer to Serializer
    from_time = serializers.DateTimeField()
    to_time = serializers.DateTimeField()

    class Meta:
        # fields = [ 'time_slots']
        pass

    def validate_time_slots(self, time_slots):
        """
        Validate each time slot in the list.
        """
        
        from_time = time_slots.get('from_time')
        to_time = time_slots.get('to_time')

        if not from_time or not to_time:
            raise serializers.ValidationError("Each slot must contain 'from_time' and 'to_time'.")

        if from_time >= to_time:
            raise serializers.ValidationError("from_time must be earlier than to_time.")

        if from_time < timezone.now():
            raise serializers.ValidationError("from_time cannot be in the past.")

        time_difference = to_time - from_time
        is_one_hour_exactly_on_hour = (
            time_difference == timedelta(hours=1) and
            from_time.minute == 0 and
            to_time.minute == 0
        )
        if not is_one_hour_exactly_on_hour:
            raise serializers.ValidationError("Each time slot must be exactly 1 hour long on the hour.")

        return time_slots

    def create(self, validated_data):
        """
        Create `AvailableTime` objects for each time slot.
        """
        doctor = self.context['user']
        doctor = DoctorProfileModel.objects.get(accounts=doctor)
        

        
        available_time = AvailableTime.objects.create(
            doctor=doctor,
            from_time=validated_data['from_time'],
            to_time=validated_data['to_time']
        )
            

        return available_time 

class AvailableTimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AvailableTime
        fields = ['from_time','to_time','status']


class AppAvailbleSerializer(AvailableTimeSerializer):
    class Meta:
        model = AvailableTime
        fields = ['from_time','to_time','status','created_at']

    
class DoctorUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='accounts.first_name', required=False)
    last_name = serializers.CharField(source='accounts.last_name', required=False)
    designation = serializers.CharField(source='accounts.designation', required=False)
    phone_number = serializers.CharField(source='accounts.phone_number', required=False)
    email = serializers.EmailField(source='accounts.email', required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = DoctorProfileModel
        fields = [
            'first_name', 'last_name', 'designation', 'phone_number', 'email', 
            'password', 'experience', 'amount', 'doctor_type', 'profile_pic'
        ]

    def validate_email(self, value):
        accounts_instance = self.instance.accounts
        if accounts_instance and accounts_instance.email != value:
            if accounts_instance.__class__.objects.filter(email=value).exclude(pk=accounts_instance.pk).exists():
                raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_phone_number(self, value):
        accounts_instance = self.instance.accounts
        if accounts_instance and accounts_instance.phone_number != value:
            if accounts_instance.__class__.objects.filter(phone_number=value).exclude(pk=accounts_instance.pk).exists():
                raise serializers.ValidationError("This phone number is already in use.")
        return value

    def update(self, instance, validated_data):
        account_data = validated_data.pop('accounts', {})
        accounts_instance = instance.accounts
        for attr, value in account_data.items():
            if attr == 'password': 
                accounts_instance.set_password(value)
            else:
                setattr(accounts_instance, attr, value)
        accounts_instance.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    

class DoctorProfileFieldEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfileFieldEdit
        fields = ['field_name', 'field_value']


class DoctorProfileModelEditSerializer(serializers.ModelSerializer):
    field_edits = DoctorProfileFieldEditSerializer(many=True)  

    doctor_name = serializers.CharField(source='accounts.accounts.username', read_only=True)
    doctor_id = serializers.IntegerField(source='accounts.id', read_only=True) 

    class Meta:
        model = DoctorProfileModelEdit
        fields = ['id', 'doctor_name','doctor_id', 'status', 'rejection_reason', 'created_at', 'field_edits','request_id']

class DeactivateDoctorSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField(required=True, help_text="ID of the doctor to deactivate.")