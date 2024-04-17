from rest_framework import serializers
from Comments.models import Comment
from User.models import User
from eBook.models import eBook

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    ebook = serializers.PrimaryKeyRelatedField(queryset=eBook.objects.all())

    class Meta:
        model = Comment
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)
