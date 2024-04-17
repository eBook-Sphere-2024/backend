from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from User.models import User
import re

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = '__all__'
        depth = 1
        
    def validate_password(self, value):
        # Check if password contains both letters and numbers
        if not re.search(r'\d', value) or not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError("Password must contain both letters and numbers.")
        return value