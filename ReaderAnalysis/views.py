from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from ReaderAnalysis.models import ReaderAnalysis
from ReaderAnalysis.serializers import ReaderSerializer
from django.contrib.auth.models import User
from eBook.models import eBook

class ReaderAnalysisAPI(APIView):

    def get(self, request):
        analyses = ReaderAnalysis.objects.all()
        serializer = ReaderSerializer(analyses, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ReaderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        analysis = get_object_or_404(ReaderAnalysis, pk=id)
        serializer = ReaderSerializer(analysis, data=request.data, partial=True)
        if serializer.is_valid():
            new_highest_progress = serializer.validated_data.get('highest_progress', analysis.highest_progress)
            if new_highest_progress > analysis.highest_progress:
                analysis.highest_progress = new_highest_progress
            
            # Update other attributes
            analysis.currentPgae = serializer.validated_data.get('currentPgae', analysis.currentPgae)
            analysis.totalPages = serializer.validated_data.get('totalPages', analysis.totalPages)
            
            analysis.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            analysis = ReaderAnalysis.objects.get(pk=int(id))  # Ensure id is converted to an integer
            analysis.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response({"error": "Invalid id. Must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)
        except ReaderAnalysis.DoesNotExist:
            return Response({"error": "ReaderAnalysis not found."}, status=status.HTTP_404_NOT_FOUND)
        
@api_view(['GET'])
def SpecificReaderAnalysis(request):
    user_id = request.query_params.get('user_id')
    ebook_id = request.query_params.get('ebook_id')
    if not user_id or not ebook_id:
        return Response({"error": "User ID and eBook ID are required"}, status=status.HTTP_400_BAD_REQUEST)
    reader_analysis = get_object_or_404(ReaderAnalysis, user_id=user_id, ebook_id=ebook_id)
    serializer = ReaderSerializer(reader_analysis)
    return Response(serializer.data)

@api_view(['GET'])
def ReaderAnalysisSpecificBook(request):
    ebook_id = request.query_params.get('ebook_id')
    if not ebook_id:
        return Response({"error": "eBook ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    reader_analysis = ReaderAnalysis.objects.filter(ebook_id=ebook_id)
    serializer = ReaderSerializer(reader_analysis, many=True)
    return Response(serializer.data)