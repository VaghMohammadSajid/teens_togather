from rest_framework import serializers
from .models import MeditationAudio,MeditationCategory

class MeditationCategorySerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    class Meta:
        model = MeditationCategory
        fields = ['id', 'name','image','about','count']
    def get_count(self,obj):
        return obj.cate.all().count()


class MeditationAudioSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    category_by_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MeditationAudio
        fields = ['id', 'title', 'audio', 'uploaded_at', 'created_by', 'category',"created_by_name",'category_by_name']
        read_only_fields = ['id', 'uploaded_at', 'created_by',]  

    def create(self, validated_data):
      
        return MeditationAudio.objects.create(**validated_data)
    
