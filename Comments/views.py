from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from Comments.models import Comment
from rest_framework import status
from Comments.serializers import CommentSerializer
from eBook.serializers import eBookSerializer
from User.serializers import RegisterSerializer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import download
from rest_framework.decorators import api_view

class CommentAPI(APIView):
    def get(self, request):
        id = request.GET.get('id')
        if id:
            comments = Comment.objects.filter(Q(ebook=id) & Q(reply_to__isnull=True))
        else:
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
        return Response(serialized_comments, status=status.HTTP_200_OK)
        
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
        update_data = {}

        if content is not None:
            update_data['content'] = content
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


@api_view(['GET'])
def get_all_replies(request):
    id = request.GET.get("id")
    ebookId = request.GET.get("ebookId")
    comments = Comment.objects.filter(reply_to__id=id, ebook=ebookId)
    serialized_comments = []
    for comment in comments:
        ebook_instance = comment.ebook
        user_instance = comment.user
        serialized_comment = CommentSerializer(comment).data
        serialized_comment['ebook'] = eBookSerializer(ebook_instance).data
        serialized_comment['user'] = RegisterSerializer(user_instance).data
        serialized_comments.append(serialized_comment)
    return Response(serialized_comments , status=status.HTTP_200_OK)

@api_view(['GET'])
def CommentAnalysis(request):
    book_id = request.GET.get('book_id')
    
    # Check if book_id is provided
    if not book_id:
        return Response({"error": "Book ID parameter (book_id) is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Filter comments by book_id
    comments = Comment.objects.filter(ebook=book_id)
    
    # Check if comments exist
    if not comments.exists():
        return Response({"error": "No comments found for the provided book ID"}, status=status.HTTP_404_NOT_FOUND)
    
    # Download the VADER lexicon
    download('vader_lexicon')
    
    # Initialize the VADER sentiment analyzer
    sia = SentimentIntensityAnalyzer()

    # Function to classify comments
    def classify_sentiment(score):
        if score['compound'] >= 0.05:
            return 'positive'
        elif score['compound'] <= -0.05:
            return 'negative'
        else:
            return 'neutral'

    # Analyze comments and classify sentiment
    positive_count = 0
    negative_count = 0

    for comment in comments:
        sentiment = sia.polarity_scores(comment.content)
        sentiment_class = classify_sentiment(sentiment)
        if sentiment_class == 'positive':
            positive_count += 1
        elif sentiment_class == 'negative':
            negative_count += 1

    total_comments = positive_count + negative_count
    positive_precision = positive_count / total_comments if total_comments else 0
    negative_precision = negative_count / total_comments if total_comments else 0

    return Response({
        "positive_precision": round(positive_precision, 2),
        "negative_precision": round(negative_precision, 2)
    }, status=status.HTTP_200_OK)