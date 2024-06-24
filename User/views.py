from django.http import JsonResponse
from Comments.models import Comment
from eBook.models import eBook
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ChangePasswordSerializer, ContactMailSerializer, LoginSerializer, RegisterSerializer , UserProfileSerializer
from django.contrib.auth import authenticate
from ReaderAnalysis.models import ReaderAnalysis
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework.parsers import MultiPartParser
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from io import BytesIO
from .serializers import PasswordResetRequestSerializer, SetNewPasswordSerializer
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string


class LoginAPI(APIView):
    def post(self, request):
        data = request.data
        serializer = LoginSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'status': False,
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data.get('username', None)
        password = serializer.validated_data.get('password', None)
        user = authenticate(username=username, password=password)

        if not user:
            return Response({
                'status': False,
                'message': "Username or password is incorrect"
            }, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            str(token)
        , status=status.HTTP_200_OK)


class UserAPI(APIView):
    def get(self, request):
        users = User.objects.filter(is_staff=False)
        serializer = RegisterSerializer(users, many=True)
        return Response({"status": "success", "users": serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        user_serializer = RegisterSerializer(data=data)
        if user_serializer.is_valid():
            try:
                # Save the user instance
                user_serializer.save()
                user_instance = user_serializer.instance
                # Create a UserProfile instance associated with the newly created user
                print(user_instance.id)
                profile_data = {'user': user_instance.id}  # user_instance.id is the ID of the newly created user
                profile_serializer = UserProfileSerializer(data=profile_data)
                if profile_serializer.is_valid():
                    profile_serializer.save()
                    username = user_serializer.validated_data.get('username', None)
                    password = user_serializer.validated_data.get('password', None)
                    user = authenticate(username=username, password=password)
                    if not user:
                        return Response({
                            'status': False,
                            'message': "Username or password is incorrect"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response(str(token),status=status.HTTP_201_CREATED)
                else:
                    # If there's an error in creating the UserProfile instance, delete the created user
                    user_instance.delete()
                    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                user_instance.delete()
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request):
        data = request.data.copy()  # Make a copy of the data to avoid modifying the original request data
        user_id = data.pop('id', None)  # Remove 'id' from the data and get its value
    
        if user_id is None:
            return Response({"status": "failed", "message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"status": "failed", "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        if User.objects.filter(username=data['username']).exclude(id=user_id).exists():
            return Response({"status": "failed", "message": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = RegisterSerializer(user, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"status": "failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        data = request.data
        user_id = data.get('id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"status": "failed", "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response({'status': "success", "message": "User deleted successfully"}, status=status.HTTP_200_OK)


class User_Profile(APIView):
    parser_classes = [MultiPartParser]
    def get(self, request):
        user_id = request.GET.get('id')
        if user_id:
            try:
                user = UserProfile.objects.get(user=user_id)
            except UserProfile.DoesNotExist:
                return Response({"status": "failed", "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"status": "failed", "message": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        user_id = request.data.get('user')
        image_profile = request.FILES.get('profile_image')
        request.data["profile_image"] = "yu12"
        try:
            user = UserProfile.objects.get(user=user_id)
        except UserProfile.DoesNotExist:
            return Response({"status": "failed", "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        response = upload_image(image_profile,user_id)  # Call upload_image function

        request.data['profile_image'] = "https://drive.google.com/thumbnail?id="+response
        # If no error, continue with serializer
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "user": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user_id = request.data.get('id')
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"status": "failed", "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Set default value for profile_image
        user.profile_image = UserProfile._meta.get_field('profile_image').get_default()
        user.save()
        
        return Response({'status': "success", "message": "profile deleted successfully"}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def get_User_by_Token(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')
    
    if authorization_header is not None:
        try:
            # Extract the token from the authorization header
            _, token_value = authorization_header.split(' ')
            token_value = token_value.replace('"', '')
            token = Token.objects.get(key=token_value)
            user = User.objects.get(id=token.user_id)
            serializer = RegisterSerializer(user)
            return Response(serializer.data)
        except (ValueError, Token.DoesNotExist):
            return Response({"error": "Invalid token"}, status=400)
    else:
        return Response({"error": "Authorization header missing"}, status=400)

class ChangePasswordAPI(APIView):
    def patch(self, request):
        data = request.data
        serializer = ChangePasswordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response({'status': 'failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetRequestView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"http://localhost:4200/resetPassword/{uidb64}/{token}"
            subject = 'Password Reset Requested'
            message = render_to_string('User/password_reset_email.txt', {
                'user': user,
                'reset_url': reset_url
            })
            send_mail(subject, message, 'ebooksphere210@gmail.com', [user.email])
        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password has been reset."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def upload_image(file, user_id):
    # Read the file data
    image_data = file.read()

    # Load credentials
    credentials_path = 'User/credential.json'
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=['https://www.googleapis.com/auth/drive.file'])

    # Build the service
    service = build('drive', 'v3', credentials=credentials)

    # Specify the folder ID where you want to upload the image
    folder_id = '1vSQghTZFfB9rMA4nWFmKTwW6g3n-e58T'

    # Check if the file already exists
    existing_file = get_existing_file(service, folder_id, user_id)
    if existing_file:
        file_id = existing_file.get('id')
        # Update the file content
        media = MediaIoBaseUpload(BytesIO(image_data), mimetype='image/jpeg')
        updated_file = service.files().update(fileId=file_id, media_body=media).execute()
        return updated_file.get("id")
    else:
        # Upload file to Google Drive within the specified folder
        file_metadata = {
            'name': user_id,
            'parents': [folder_id]  # Specify the folder ID as the parent
        }
        media = MediaIoBaseUpload(BytesIO(image_data), mimetype='image/jpeg')
        uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return uploaded_file.get("id")

def get_existing_file(service, folder_id, user_id):
    # Search for the file by name within the specified folder
    query = f"name='{user_id}' and '{folder_id}' in parents and trashed=false"
    response = service.files().list(q=query, fields='files(id)').execute()
    files = response.get('files', [])
    if files:
        return files[0]  # Return the first matching file
    else:
        return None  # No existing file found

@api_view(['GET'])
def GetBookAnalyticsNumbers(request):
    author_id = request.GET.get('author_id')
    if not author_id:
        return Response({'message': 'author_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    book_id = request.GET.get('book_id')
    if not author_id and not book_id:
        return Response({'message': 'author_id and book_id are required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        eBooks = eBook.objects.filter(author=author_id)
        Readers = 0
        comments = 0
        for book in eBooks:
            Readers += ReaderAnalysis.objects.filter(ebook=book).count()
            comments += Comment.objects.filter(ebook=book).count()
        Readers= ReaderAnalysis.objects.filter(ebook=book_id).count()
        comments = Comment.objects.filter(ebook=book_id).count()
        return Response({'comments': comments, 'eBooks': eBooks.count(), 'Readers': Readers}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['POST'])
def ContactMail(request):
    serializer = ContactMailSerializer(data=request.data)
    if serializer.is_valid():
    # Send email
        name = serializer.validated_data['name']
        email = serializer.validated_data['email']
        subject = serializer.validated_data['subject']
        message = serializer.validated_data['message']
        full_message = f"Message from {name} <{email}>:\n\n{message}"
        send_mail(
            subject,
            full_message,
            '{{email}}',  
            ['ebooksphere210@gmail.com'],  
            fail_silently=False,
            )
        return Response({"message": "Email sent successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)