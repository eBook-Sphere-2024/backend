from rest_framework import serializers
from .models import eBook, Category

class eBookSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    class Meta:
        model = eBook
        fields = '__all__'
        depth = 1

    def validate(self, data):
        categories = data.get('categories')
        if not categories or len(categories) < 1:
            raise serializers.ValidationError("At least one category is required for an eBook.")
        return data
    
class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = '__all__'