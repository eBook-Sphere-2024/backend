from django.shortcuts import render
from rest_framework.decorators import api_view
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from eBook.models import eBook
from eBook.serializers import eBookSerializer
from search.semanticSearch import *


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
    
    
class related_eBook_API(APIView):
    def get(self , reuest ):
        query = reuest.GET.get('query')
        print(query)
        if query:
            results = search_eBook(query)
            for hit in results:
                print(hit['_score'], hit['_source']['filename'])
            return Response({"status": "success"}, status.HTTP_200_OK)
        else:
            return Response({"error": "No search query provided"}, status.HTTP_400_BAD_REQUEST)
        

class IndexAPIView(APIView):
    def get(self, request):
        index_eBook()
        return Response({"status": "success"}, status=status.HTTP_200_OK)
        