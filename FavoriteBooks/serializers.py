# serializers.py
from rest_framework import serializers
from .models import FavoriteBooks
from django.contrib.auth.models import User
from eBook.models import eBook

class FavoriteBooksSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    ebook_id = serializers.PrimaryKeyRelatedField(queryset=eBook.objects.all(), source='ebook', write_only=True)

    class Meta:
        model = FavoriteBooks
        fields = '__all__'

    def create(self, validated_data):
        return FavoriteBooks.objects.create(**validated_data)
