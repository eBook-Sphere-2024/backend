import io
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from Template.models import Template
from Template.serializers import TemplateSerializer
from rest_framework import status
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


class TemplateAPI(APIView):
    def get(self, request):
        templates = Template.objects.all()
        serializer = TemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = TemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "Templates": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "failed", "Templates": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        data = request.data
        obj = Template.objects.get(id=data['id'])
        serializer = TemplateSerializer(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "Templates": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "failed", "Templates": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        comment = get_object_or_404(Template, id=request.data.get('id'))
        comment.delete()
        return Response(status=status.HTTP_200_OK)
    
def authenticate_drive_service():
    # Initialize the Google Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'Template/credential.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return credentials

def get_content(file_id, drive_service):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:  # Loop until complete
        status, done = downloader.next_chunk()
    fh.seek(0)  # Move the file pointer to the beginning (reset)
    return fh.read()

class getTemplateById(APIView):
    def get(self, request):
        file_id = request.GET.get('id')
        credentials = authenticate_drive_service()
        drive_service = build('drive', 'v3', credentials=credentials)

        try:
            content = get_content(file_id, drive_service)
            return HttpResponse(content, content_type='application/octet-stream')
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)