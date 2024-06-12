from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import FavoriteBooks
from .serializers import FavoriteBooksSerializer
from django.contrib.auth.models import User
from eBook.models import eBook
class FavoriteBooksAPI(APIView):

    def get(self, request):
        user_id = request.query_params.get('user_id')  # Get the user ID from query parameters
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        favorite_books = FavoriteBooks.objects.filter(user_id=user_id)
        serialized_books = FavoriteBooksSerializer(favorite_books, many=True)
        return Response(serialized_books.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        user_id = data.get('user_id')
        ebook_id = data.get('ebook_id')

        if not user_id or not ebook_id:
            return Response({"error": "User ID and eBook ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        ebook = get_object_or_404(eBook, id=ebook_id)
        
        # Check if this favorite already exists to avoid duplicates
        if FavoriteBooks.objects.filter(user=user, ebook=ebook).exists():
            return Response({"error": "This book is already in the favorites list"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the FavoriteBooks instance directly with user and ebook IDs
        favorite_book = FavoriteBooks.objects.create(user_id=user_id, ebook_id=ebook_id)

        serializer = FavoriteBooksSerializer(favorite_book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



    def delete(self, request):
        user_id = request.data.get('user_id')
        ebook_id = request.data.get('ebook_id')
        if not user_id or not ebook_id:
            return Response({"error": "User ID and eBook ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        favorite_book = get_object_or_404(FavoriteBooks, ebook_id=ebook_id, user_id=user_id)
        favorite_book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
