from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from Comments.models import Comment
from rest_framework import status
from Comments.serializers import CommentSerializer
from eBook.serializers import eBookSerializer
from User.serializers import RegisterSerializer

class CommentAPI(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serialized_comments = []
        for comment in comments:
            # Retrieve associated eBook and user instances
            ebook_instance = comment.ebook
            user_instance = comment.user

            # Serialize comment, eBook, and user instances
            serialized_comment = CommentSerializer(comment).data
            serialized_comment['ebook'] = eBookSerializer(ebook_instance).data
            serialized_comment['user'] = RegisterSerializer(user_instance).data
            
            # Append serialized comment to the list
            serialized_comments.append(serialized_comment)
        
        # Return response without .data
        return Response({"status": "success", "comments": serialized_comments}, status=status.HTTP_200_OK)
        
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

