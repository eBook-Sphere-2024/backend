from requests import Response
from rest_framework import serializers
from User.models import UserProfile
from rest_framework import status
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import  force_str
from django.contrib.auth.tokens import default_token_generator
from django.db.models.functions import Lower
from django.db.models import Q

class RegisterSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)

    def validate(self, data):
        instance_id = self.instance.id if self.instance else None
        username = data['username']
        if 'username' in data and User.objects.annotate(username_lower=Lower('username')).filter(Q(username__iexact=username) & ~Q(id=instance_id)).exists():
            raise serializers.ValidationError('Username already exists')
        if 'email' in data and User.objects.filter(email=data['email']).exclude(id=instance_id).exists():
            raise serializers.ValidationError('Email already exists')
        if 'password' in data and len(data['password']) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long')
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()
        if user is None:
            raise serializers.ValidationError('User does not exist')
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError('Old password is incorrect')
        return data

    def save(self, **kwargs):
        user = User.objects.get(username=self.validated_data['username'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("There is no user registered with this email address.")
        return value

class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def save(self, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(self.validated_data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or user ID.")

        if not default_token_generator.check_token(user, self.validated_data['token']):
            raise serializers.ValidationError("Invalid token or user ID.")

        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    
class ContactMailSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    subject = serializers.CharField()
    message = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        depth = 1


