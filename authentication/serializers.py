from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    # Das Feld für die Bestätigung definieren (write_only, damit es nicht in der Response landet)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        # 1. Prüfen, ob Passwörter übereinstimmen
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Die Passwörter stimmen nicht überein."})
        
        # 2. Prüfen, ob die E-Mail bereits existiert
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Diese E-Mail-Adresse wird bereits verwendet."})
        
        return attrs

    def create(self, validated_data):
        # password_confirm entfernen, da das User-Model dieses Feld nicht besitzt
        validated_data.pop('password_confirm')
        
        # User sicher anlegen (create_user sorgt dafür, dass das Passwort gehasht wird!)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user