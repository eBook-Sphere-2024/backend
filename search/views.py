from django.shortcuts import render
from rest_framework.decorators import api_view
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from eBook.models import eBook
from eBook.serializers import CategorySerializer, eBookSerializer
from django.contrib.auth.models import User
from User.serializers import RegisterSerializer
from search.semanticSearch import *



class searchAPI(APIView):
    def get(self, request):
        query = request.GET.get('query')
        if query:
            # Normalize query to lowercase and remove extra spaces
            query_lower = query.lower().strip()
            
            # Split query into words
            query_words = query_lower.split()

            # Perform the initial search query (case-insensitive)
            results = eBook.objects.filter(
                Q(title__icontains=query_lower) | Q(author__username__icontains=query_lower)
            )
            
            results = results.filter(is_reviewed=True)
            
            filtered_results = []
            
            # Filter results based on the criteria
            for ebook in results:
                title_lower = ebook.title.lower()
                author_lower = ebook.author.username.lower()
                
                # Check if any word in query is in title or author
                if all(any(word in field for field in [title_lower, author_lower]) for word in query_words):
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
                    
                    eBooks = eBook.objects.filter(content=hit['_source']['fileId'])
                    print(eBooks)
                    if eBooks:  # Check if any eBooks are found
                        serializer = eBookSerializer(eBooks, many=True)
                        serialized_data_with_score = [{"score": hit['_score'], "eBook": eBook_data} for eBook_data in serializer.data]
                        eBooks_data.extend(serialized_data_with_score)

                sorted_eBooks = sorted(eBooks_data, key=lambda x: x['score'], reverse=True)
                sorted_eBooks_without_score = [eBook_data['eBook'] for eBook_data in sorted_eBooks]
                serialized_ebooks = []
                for ebook in sorted_eBooks_without_score:
                    ebook = eBook.objects.get(id=ebook['id'])
                    author_instance = ebook.author
                    categories = ebook.categories.all()
                    serialized_ebook = eBookSerializer(ebook).data
                    serialized_ebook['categories'] = CategorySerializer(categories, many=True).data
                    serialized_ebook['author'] = RegisterSerializer(author_instance).data
                    serialized_ebooks.append(serialized_ebook)
                return Response(serialized_ebooks, status=status.HTTP_200_OK)

            except RuntimeError as e:
                return Response({"status": "failed", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "No search query provided"}, status=status.HTTP_400_BAD_REQUEST)

class IndexAPIView(APIView):
    def get(self, request):
        fileId = request.GET.get('fileId')
        index_one_ebook(fileId)
        return Response({"status": "success"}, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def indexAll(request):
    index_eBooks()
    return Response({"status": "success"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def deleteIndex(request):
    delete_index()
    return Response({"status": "success"}, status=status.HTTP_200_OK)