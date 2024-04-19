from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LoginSerializer, RegisterSerializer , UserProfileSerializer
from django.contrib.auth import authenticate
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
        return Response({
            'status': True,
            'message': "Login successful",
            'token': str(token),
            'user_id': user.id ,
            'date': str(user.date_joined)
        }, status=status.HTTP_200_OK)


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
                    return Response({"status": "success", "user": user_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    # If there's an error in creating the UserProfile instance, delete the created user
                    user_instance.delete()
                    return Response({"status": "failed", "errors": profile_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                user_instance.delete()
                return Response({"status": "failed", "errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "failed", "errors": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request):
        data = request.data
        user_id = data.get('id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"status": "failed", "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RegisterSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "user": serializer.data}, status=status.HTTP_200_OK)
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
        users = UserProfile.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return Response({"status": "success", "users": serializer.data}, status=status.HTTP_200_OK)

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