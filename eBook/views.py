from django.shortcuts import get_object_or_404
from .models import eBook, Category
from .command import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from eBook.serializers import eBookSerializer , CategorySerializer

class EbookAPI(APIView):

    def get(self, request ):
        ebook_id = request.GET.get('id')
        if not ebook_id:
            command = ShowBooksCommand()
            ebooks_data = command.execute()
            return Response({"status": "success", "ebooks": ebooks_data}, status=status.HTTP_200_OK)
        else:
            command = ShowEbookDetailsCommand(ebook_id)
            ebook_data = command.execute()
            return Response(ebook_data, status=status.HTTP_200_OK)
    
    def post(self, request):
        command = CreateEbookCommand(request.data)
        result = command.execute()
        if isinstance(result, dict):
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        ebook_id = request.data.get('id')
        command = EditEbookCommand(ebook_id, request.data)
        success,message, data_or_errors = command.execute()
        if success:
            return Response({'message': message, 'data_or_errors': data_or_errors},status.HTTP_200_OK)
        return Response({'message': message, 'data_or_errors': data_or_errors},status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
       ebook = get_object_or_404(eBook, id=request.data.get('id'))
       command = DeleteEbookCommand(ebook.id)
       command.execute()
       return Response(status=status.HTTP_200_OK)


class EbookCategoryAPI(APIView):

    def get(self, request):
        command = ShowCategoriesCommand()
        categories_data = command.execute()
        return Response({"status": "success", "categories": categories_data}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def filter_books_by_category(request):
    category_id = request.GET.get('id')
    try:
        category = Category.objects.get(pk=category_id)
        command = FilterBooksByCategoryCommand(category_id)
        ebooks_data = command.execute()
        serializer = eBookSerializer(ebooks_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)