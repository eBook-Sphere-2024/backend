from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from Template.models import Template
from Template.serializers import TemplateSerializer
from rest_framework import status

class TemplateAPI(APIView):
    def get(self, request):
        templates = Template.objects.all()
        serializer = TemplateSerializer(templates, many=True)
        return Response({"status": "success", "Templates": serializer.data}, status=status.HTTP_200_OK)
    
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