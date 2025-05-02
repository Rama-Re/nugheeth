from rest_framework import serializers
from .models import User, PilgrimProfile, EmergencyProfile, FamilyProfile, NormalProfile
from .models import VerificationCode


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'fcm_token',
            'phone_number', 'account_type', 'profile_image', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'fcm_token': {'required': False},
            'email': {'required': False},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class PilgrimProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PilgrimProfile
        fields = ['id', 'user', 'health_id', 'id_or_pass_number', 'medical_info', 'campaign_number']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class EmergencyProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = EmergencyProfile
        fields = ['id', 'user', 'user_email', 'is_active']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class FamilyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyProfile
        fields = ['id', 'user', 'pilgrim']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class NormalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalProfile
        fields = ['id', 'user']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = ['user', 'code', 'purpose', 'created_at', 'updated_at']
