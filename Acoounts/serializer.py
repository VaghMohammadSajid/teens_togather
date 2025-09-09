from rest_framework import serializers
from .models import Concentrate,Avatar,Accounts,TeenagerAndParent,FeatureToggles


class ConcentrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concentrate
        fields = ['id', 'name']
        read_only_fields = ['id']

    def create(self, validated_data):
        return Concentrate.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return Concentrate.objects.update(**validated_data)
    
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='account.email', read_only=True)
    phone_number = serializers.CharField(source='account.phone_number', read_only=True)
    designation = serializers.CharField(source='account.designation', read_only=True)

    class Meta:
        model = TeenagerAndParent
        fields = ['email', 'phone_number', 'designation', 'date_of_birth', 'gender', 'nick_name','avatar']

class UpdateAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.PrimaryKeyRelatedField(queryset=Avatar.objects.all())

    class Meta:
        model = TeenagerAndParent
        fields = ['avatar']
        
class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ['id', 'image']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Accounts

class AccountPartialSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['first_name','last_name','username','email','phone_number','date_joined','last_login','is_active','designation']
        model = Accounts

class TeensAndParentSerializer(serializers.ModelSerializer):
    account = AccountPartialSerializer()
    class Meta:
        fields = "__all__"
        model = TeenagerAndParent

class UserCountSerializer(serializers.Serializer):
    total_teens = serializers.IntegerField()
    total_parents = serializers.IntegerField()
    total_doctors = serializers.IntegerField()

class FeatureTogglesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureToggles
        fields = '__all__'  