from django.shortcuts import render
from rest_framework.decorators import api_view
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from eBook.models import eBook
from eBook.serializers import eBookSerializer

class searchAPI(APIView):
    def get(self, request):
        query = request.GET.get('query')
        if query:
            results = eBook.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )
            serializer = eBookSerializer(results, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No search query provided"}, status=400)
    
    
