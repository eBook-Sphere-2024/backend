from rest_framework import serializers
from ReaderAnalysis.models import ReaderAnalysis
from django.contrib.auth.models import User
from eBook.models import eBook

class ReaderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    ebook = serializers.PrimaryKeyRelatedField(queryset=eBook.objects.all())
    
    class Meta:
        model = ReaderAnalysis
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        return ReaderAnalysis.objects.create(**validated_data)
