from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def direct_search(request):
    return Response({"message": "Direct search performed"})

@api_view(['GET'])
def InDirect_search(request):
    return Response({"message": "InDirect search performed"})
