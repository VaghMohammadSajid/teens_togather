from rest_framework import serializers

from .models import HappyMoments,HappyMomentReport
from rest_framework.validators import ValidationError
from Acoounts.serializer import AccountSerializer
from Acoounts.models import TeenagerAndParent


class HappyMomentsSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField(read_only=True)
    
    publish_by = serializers.SerializerMethodField()  
    person_likes = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = HappyMoments
        fields = '__all__'
        extra_kwargs = {'publish_by': {'read_only': True}}

    def get_is_liked(self,obj):
        user = self.context['user']
        teen_obj = TeenagerAndParent(account=user)
        if  teen_obj in   obj.person_likes.all():
            return True
        else:
            return False
    def get_person_likes(self,obj):
        return [x.account.username for x in obj.person_likes.all()]

    def get_publish_by(self, obj):
        return obj.publish_by.nick_name if obj.publish_by else None
    
    def create(self, validated_data):
        user = self.context['user']
        try:
            teenager_obj = TeenagerAndParent.objects.get(account=user)
        except:
            raise ValidationError({'error':'You are not a teenager or parent'})
        validated_data['publish_by'] = teenager_obj
        
        voice_of_the_day = HappyMoments.objects.create(**validated_data)
        return voice_of_the_day
    
class HappyMomentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = HappyMomentReport
        fields = ['user', 'happy_moment', 'title', 'description', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context.get('user') 
        return super().create(validated_data)  
    
class HappyMomentReportSerializertwo(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')  # Include the username instead of user ID
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model = HappyMomentReport
        fields = ['user', 'title', 'description', 'created_at']


class HappyMomentSerializer(serializers.ModelSerializer):
    reports = HappyMomentReportSerializertwo(many=True)
    report_count = serializers.SerializerMethodField()

    class Meta:
        model = HappyMoments
        fields = ['id','title', 'report_count', 'reports']

    def get_report_count(self, obj):
        # Count the number of reports for each HappyMoment
        return HappyMomentReport.objects.filter(happy_moment=obj).count()