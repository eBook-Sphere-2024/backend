from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LoginSerializer, RegisterSerializer , UserProfileSerializer
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import UserProfile

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
        user_id = request.data.get('id')
        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"status": "failed", "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
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