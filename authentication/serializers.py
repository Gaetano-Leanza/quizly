from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User

        fields = ('username', 'email', 'password', 'confirmed_password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, attrs):

        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError(
                {"password": "Die Passwörter stimmen nicht überein."})

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "Diese E-Mail-Adresse wird bereits verwendet."})

        return attrs

    def create(self, validated_data):

        validated_data.pop('confirmed_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
