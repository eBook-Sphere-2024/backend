from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from Comments.models import Comment
from rest_framework import status
from Comments.serializers import CommentSerializer

class CommentAPI(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response({"status": "success", "Comments": serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        data = request.data
        obj = Comment.objects.get(id=data['id'])
        serializer = CommentSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "Comments": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "failed", "Comments": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        comment = get_object_or_404(Comment, id=request.data.get('id'))
        comment.delete()
        return Response(status=status.HTTP_200_OK)
