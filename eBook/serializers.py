from rest_framework import serializers
from django.contrib.auth.models import User

from Template.models import Template
from .models import eBook, Category

class eBookSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    template = serializers.PrimaryKeyRelatedField(queryset=Template.objects.all())
    class Meta:
        model = eBook
        fields = '__all__'
        depth = 1

    def validate(self, data):
        categories = data.get('categories')
        if not categories or len(categories) < 1:
            raise serializers.ValidationError("At least one category is required for an eBook.")
        elif 'author' not in data:
            raise serializers.ValidationError("Author is required.")
        return data
    
class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = '__all__'