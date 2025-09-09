from rest_framework import serializers
from Acoounts.models import Concentrate, TeenagerAndParent
from Voice_of_the_day.models import VoiceOfTheDay
from rest_framework.validators import ValidationError
from Acoounts.serializer import AccountSerializer


class ConcentrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concentrate
        fields = ['id', 'name']
    

class VoiceOfTheDayLimitedSerializer(serializers.ModelSerializer):
    publish_by = serializers.SerializerMethodField()
    class Meta:
        model = VoiceOfTheDay
        fields = ['title', 'content','image','publish_by','create_date']

    def get_publish_by(self, obj):
        return f'{obj.publish_by.first_name} {obj.publish_by.last_name}'  if obj.publish_by else None           

class VoiceOfTheDayUpdateSerializer(serializers.ModelSerializer):
    concentrates = ConcentrateSerializer(many=True, read_only=True)
    publish_by = serializers.SerializerMethodField()
    
    person_likes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VoiceOfTheDay
        fields = '__all__'
        extra_kwargs = {'publish_by': {'read_only': True}}

    def get_person_likes(self,obj):
        return [x.account.username for x in obj.person_likes.all()]

    def get_publish_by(self, obj):
        
        return obj.publish_by.username if obj.publish_by else None

    



class VoiceOfTheDayLimitedSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceOfTheDay
        fields = ['id','title', 'image', 'create_date']  # Specify the fields you want




class VoiceOfTheDaySerializer(VoiceOfTheDayUpdateSerializer):

    is_liked = serializers.SerializerMethodField(read_only=True)
    def get_is_liked(self,obj):
        user = self.context['user']
        teen_obj = TeenagerAndParent(account=user)
        if  teen_obj in   obj.person_likes.all():
            return True
        else:
            return False
    
    def validate(self, data):
        print(data)
        try:
            if data['title'] == None:
                raise serializers.ValidationError("Title Required")
        except KeyError:
            raise serializers.ValidationError("Title Required")
        try:
            if data['content'] == None:
                raise serializers.ValidationError("Content Required")  
        except KeyError:
            raise serializers.ValidationError("Content Required")
        try:
            if data['image'] == None:
                raise serializers.ValidationError("image Required")      
        except KeyError:
            raise serializers.ValidationError("image Required")
        return data
            
    def create(self, validated_data):
        

        concentrate_int_list = self.context['concentratesss']
        
        user = self.context['user']
        validated_data['publish_by'] = user
        

        
        
        voice_of_the_day = VoiceOfTheDay.objects.create(**validated_data)
        
        
        voice_of_the_day.concentrates.add(*concentrate_int_list)
        voice_of_the_day.save()
    

        return voice_of_the_day
    

