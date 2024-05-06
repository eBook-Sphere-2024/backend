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
            if 'reply_to' in serializer.validated_data:
                parent_comment = Comment.objects.get(pk=serializer.validated_data['reply_to'].id)
                if parent_comment.ebook != serializer.validated_data['ebook']:
                    return Response({"error": "Reply must be on the same ebook"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        data = request.data
        id = request.GET.get('id')
        try:
            obj = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            return Response({"status": "failed", "message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        content = data.get('content')
        likes = data.get('likes')
        print(content, likes)
        update_data = {}

        if content is not None:
            update_data['content'] = content
        if likes is not None:
            update_data['likes'] = likes
        if update_data == {}:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CommentSerializer(obj, data=update_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "Comments": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "failed", "Comments": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        id = request.GET.get('id')
        comment = get_object_or_404(Comment, id=id)
        for reply in comment.replies.all():
            self.delete_replies(reply)
            reply.delete()
        comment.delete()
        return Response(status=status.HTTP_200_OK)
    
    def delete_replies(self, comment):
        # Recursively delete all replies to the given comment
        for reply in comment.replies.all():
            self.delete_replies(reply)
            reply.delete()

