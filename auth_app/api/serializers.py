from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user registration. 
    Validates user input including password matching and email uniqueness,
    and handles secure user creation.
    """

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User

        fields = ('username', 'email', 'password', 'confirmed_password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        """
        Validates that passwords match and the email address is not already taken.
        """

        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "This email address is already in use."})

        return attrs

    def create(self, validated_data):
        """
        Removes the confirmation password and creates a new user with hashed password.
        """

        validated_data.pop('confirmed_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user