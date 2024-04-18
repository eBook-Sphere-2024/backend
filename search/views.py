from django.shortcuts import render
from rest_framework.decorators import api_view
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from eBook.models import eBook
from eBook.serializers import eBookSerializer
from django.contrib.auth.models import User
from User.serializers import RegisterSerializer
from search.semanticSearch import *



class searchAPI(APIView):
    def get(self, request):
        query = request.GET.get('query')
        if query:
            # Perform the search query
            results = eBook.objects.filter(
                Q(title__icontains=query) | Q(author__username__icontains=query)
            )

            # Retrieve the user instances for the authors of the eBooks
            user_ids = results.values_list('author', flat=True)
            users = User.objects.filter(id__in=user_ids)

            # Serialize eBook and its author
            ebook_serializer = eBookSerializer(results, many=True)
            user_serializer = RegisterSerializer(users, many=True)

            # Add author data to eBook serializer
            for ebook_data in ebook_serializer.data:
                author_id = ebook_data['author']
                author_data = next((user for user in user_serializer.data if user['id'] == author_id), None)
                if author_data:
                    ebook_data['author'] = author_data

            return Response(ebook_serializer.data)
        else:
            return Response({"error": "No search query provided"}, status=status.HTTP_400_BAD_REQUEST)
        
class RelatedEBookAPI(APIView):
    def get(self, request):
        query = request.GET.get('query')
        if query:
            try:
                results = search_eBook(query)
                response_data = []
                for hit in results:
                    # Filter eBook instances by filename
                    eBooks = eBook.objects.filter(content=hit['_source']['filename'])
                    if eBooks:  # Check if any eBooks are found
                        serializer = eBookSerializer(eBooks, many=True)
                        response_data.append({"score": hit['_score'], "eBooks": serializer.data})
                return Response({"status": "success", "results": response_data}, status=status.HTTP_200_OK)
            except RuntimeError as e:
                return Response({"status": "failed", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "No search query provided"}, status=status.HTTP_400_BAD_REQUEST)

class IndexAPIView(APIView):
    def get(self, request):
        index_eBook()
        return Response({"status": "success"}, status=status.HTTP_200_OK)

