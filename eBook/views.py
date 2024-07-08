import os
from tokenize import Comment
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import eBook, Category, Rating
from .command import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from eBook.serializers import eBookSerializer , RatingSerializer
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from django.db.models import Avg
from eBook.utility import *


class EbookAPI(APIView):

    def get(self, request ):
        ebook_id = request.GET.get('id')
        if not ebook_id:
            command = ShowBooksCommand()
            ebooks_data = command.execute()
            return Response(ebooks_data, status=status.HTTP_200_OK)
        else:
            command = ShowEbookDetailsCommand(ebook_id)
            ebook_data = command.execute()
            if(ebook_data is None):
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(ebook_data, status=status.HTTP_200_OK)
    
    def post(self, request):
        command = CreateEbookCommand(request.data)
        result = command.execute()
        if isinstance(result, dict):
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        ebook_id = request.data.get('id')
        command = EditEbookCommand(ebook_id, request.data)
        success,message, data_or_errors = command.execute()
        if success:
            return Response({'message': message, 'data_or_errors': data_or_errors},status.HTTP_200_OK)
        return Response({'message': message, 'data_or_errors': data_or_errors},status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
       id = request.query_params.get('id')
       ebook = eBook.objects.get(id=id)
       command = DeleteEbookCommand(ebook.id)
       command.execute()
       return Response(status=status.HTTP_200_OK)


class EbookCategoryAPI(APIView):

    def get(self, request):
        command = ShowCategoriesCommand()
        categories_data = command.execute()
        return Response(categories_data, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def filter_books_by_category(request):
    category_id = request.GET.get('id')
    try:
        category = Category.objects.get(pk=category_id)
        command = FilterBooksByCategoryCommand(category_id)
        ebooks_data = command.execute()
        
        serialized_ebooks = []
        for ebook in ebooks_data:
            author_instance = ebook.author
            categories = ebook.categories.all()
            serialized_ebook = eBookSerializer(ebook).data
            serialized_ebook['categories'] = CategorySerializer(categories, many=True).data
            serialized_ebook['author'] = RegisterSerializer(author_instance).data
            serialized_ebooks.append(serialized_ebook)

        return Response(serialized_ebooks, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def download_file_from_google_drive(request):
    file_id = request.data.get('fileId')
    if not file_id:
        return Response({"error": "fileId is required"}, status=status.HTTP_400_BAD_REQUEST)
    # Define the path to your service account JSON key file
    service_account_file = 'eBook/credential.json'
    # Authenticate the application with Google Drive API using service account credentials
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)
    try:
        # Get the file metadata
        file_metadata = service.files().get(fileId=file_id).execute()
        # Get the file name
        file_name = file_metadata['name']
        # Construct the download link
        download_link = f"https://drive.google.com/uc?id={file_id}&export=download"   
        return Response(download_link)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class AuthorBooksAPI(APIView):

    def get(self, request):
        author_id = request.GET.get('id')
        if author_id:
            try:
                books = eBook.objects.filter(author=author_id,is_reviewed=True)
                serializer = eBookSerializer(books, many=True)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Author ID is required"}, status=status.HTTP_400_BAD_REQUEST)

class RatingBooksAPI(APIView):
    # get rating by ebookid
    def get(self, request):
        ebook_id = request.GET.get('id')
        if not ebook_id:
            return Response({"error": "ebook_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        ebook = get_object_or_404(eBook, id=ebook_id)
        ratings = Rating.objects.filter(ebook=ebook)
        
        # Calculate the average rating value
        average_rating = ratings.aggregate(Avg('rate'))['rate__avg']
        return Response(average_rating, status=status.HTTP_200_OK)
    
    def put(self, request):
        ebook_id = request.data.get('ebook')
        user_id = request.data.get('user')
        rating_value = request.data.get('rate')
        
        if not (ebook_id and user_id and rating_value):
            return Response({"error": "ebook_id, user_id, and rate are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        ebook = get_object_or_404(eBook, id=ebook_id)
        user = get_object_or_404(User, id=user_id)
        
        # Check if the rating already exists for the given user and ebook
        rating, created = Rating.objects.get_or_create(ebook=ebook, user=user)
        
        # Update the rating value
        rating.rate = rating_value
        rating.save()
        
        return Response({"message": "Rating added successfully"}, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def publish(request):
    try:
        # Extract data from request
        pdf_file = request.FILES.get('pdfFile')
        author_id = request.data.get('authorId')  
        ebook_title = request.data.get('ebookTitle')  
        description = request.data.get('description')
        selected_categories = request.data.getlist('categories', []) 
        user = User.objects.get(id=author_id)
        folderId = '1SMPcRVyp1y36Tqxyxgt0wD5zItzzOKoC'
        coverFolderId = '1bU5DarU3VxuMsMppm9dcm7VrwXq_dJYn'
        fileId = uploadEbookForReview(pdf_file,folderId,ebook_title)
        coverId = process_and_upload_cover_image(fileId, folderId, coverFolderId, ebook_title)
        coverId = "https://drive.google.com/thumbnail?id="+coverId
        # Create eBook data dictionary
        ebook_data = {
            'title': ebook_title,
            'author': user.id,
            'description': description,
            'content': fileId,
            'cover': coverId,
            'is_reviewed': False  ,
            'categories': selected_categories
        }
        # Serialize the eBook data
        serializer = eBookSerializer(data=ebook_data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'eBook published successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'message': 'An unexpected error occurred. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(['GET'])
def get_ebook_content(request):
    ebook_id = request.GET.get('id')
    if not ebook_id:
        return Response({'message': 'ebook_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    ebook = get_object_or_404(eBook, id=ebook_id)
    try:
        content = get_content(ebook.content)
        return HttpResponse(content, content_type='application/pdf')
    except Exception as e:
        return Response({'message': 'An unexpected error occurred. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
