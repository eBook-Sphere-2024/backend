import os
from django.shortcuts import get_object_or_404
from .models import eBook, Category
from .command import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from eBook.serializers import eBookSerializer 
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload

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
       ebook = get_object_or_404(eBook, id=request.data.get('id'))
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
        serializer = eBookSerializer(ebooks_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def download_file_from_google_drive(request):
    file_id = request.data.get('fileId')
    local_path = request.data.get('localPath')
    if not file_id or not local_path:
        return Response({"error": "Both fileId and localPath are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Define the path to your service account JSON key file
    service_account_file = 'eBook/credential.json'
    
    # Authenticate the application with Google Drive API using service account credentials
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)
    
    try:
        # Download the PDF file
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(local_path, mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            prograss, done = downloader.next_chunk()
            print("Download %d%%." % int(prograss.progress() * 100))
        print("Download Complete!")
        fh.close()  # Close the file handle after download is complete
        return Response({"message": "Download successful"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)