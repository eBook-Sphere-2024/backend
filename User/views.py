from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from User.models import User
from .serializers import LoginSerializer, UserSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class LoginAPI(APIView):
    def post(self, request):
        data = request.data
        serializer = LoginSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'Status': False,
                'Message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data.get('username', None)
        password = serializer.validated_data.get('password', None)
        print("Received username:", username)
        print("Received password:", password)

        user = authenticate(username=serializer.data['username'], password=serializer.data['password'])
        print("Authenticated user:", user)

        if not user:
            return Response({
                'Status': False,
                'Message': "Username or password is incorrect"
            }, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'Status': True,
            'Message': "Login successful",
            'Token': str(token)
        }, status=status.HTTP_200_OK)


class UserAPI(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({"status": "success", "Users": serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "Users": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "failed", "Users": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self,request):
        data= request.data
        obj = User.objects.get(id=data['id'])
        serializer = UserSerializer(obj,data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "Users": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "failed", "Users": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        data= request.data
        obj = User.objects.get(id=data['id'])
        obj.delete()
        return Response({'massage':"This user is deleted successfully"},status=status.HTTP_200_OK)
