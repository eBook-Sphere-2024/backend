from rest_framework import serializers
from django.contrib.auth.models import User
from .models import eBook, Category, Rating

class eBookSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = eBook
        fields = '__all__'
        depth = 1

    def validate(self, data):
        if 'categories' in data and (not data['categories'] or len(data['categories']) < 1):
            raise serializers.ValidationError("At least one category is required for an eBook.")
        return data
    
class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'