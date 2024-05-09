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
            # Convert query to lowercase
            query_lower = query.lower()

            # Perform the search query
            results = eBook.objects.filter(
                Q(title__icontains=query_lower) | Q(author__username__icontains=query_lower)
            )
            

            # Filter results based on the criteria
            filtered_results = []
            for ebook in results:
                title_lower = ebook.title.lower()
                author_lower = ebook.author.username.lower()
                if len(title_lower.split()) == 1 and len(author_lower.split()) == 1:
                    if title_lower.startswith(query_lower) or author_lower.startswith(query_lower):
                        filtered_results.append(ebook)
                else:
                    title_words = title_lower.split()
                    author_words = author_lower.split()
                    title_matches = any(word.startswith(query_lower) for word in title_words)
                    author_matches = any(word.startswith(query_lower) for word in author_words)
                    if title_matches or author_matches:
                        filtered_results.append(ebook)

            # Retrieve the user instances for the authors of the eBooks
            user_ids = [ebook.author.id for ebook in filtered_results]
            users = User.objects.filter(id__in=user_ids)

            # Serialize eBook and its author
            ebook_serializer = eBookSerializer(filtered_results, many=True)
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
                eBooks_data = []

                for hit in results:
                    # Filter eBook instances by filename
                    eBooks = eBook.objects.filter(title=hit['_source']['filename'][:-len('.pdf')])

                    if eBooks:  # Check if any eBooks are found
                        serializer = eBookSerializer(eBooks, many=True)
                        serialized_data_with_score = [{"score": hit['_score'], "eBook": eBook_data} for eBook_data in serializer.data]
                        eBooks_data.extend(serialized_data_with_score)

                sorted_eBooks = sorted(eBooks_data, key=lambda x: x['score'], reverse=True)
                sorted_eBooks_without_score = [eBook_data['eBook'] for eBook_data in sorted_eBooks]

                return Response(sorted_eBooks_without_score, status=status.HTTP_200_OK)

            except RuntimeError as e:
                return Response({"status": "failed", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "No search query provided"}, status=status.HTTP_400_BAD_REQUEST)

class IndexAPIView(APIView):
    def get(self, request):
        fileId = request.GET.get('fileId')
        index_one_ebook(fileId)
        return Response({"status": "success"}, status=status.HTTP_200_OK)
    