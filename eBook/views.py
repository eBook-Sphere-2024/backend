from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import eBook, Category,eBookCategory
from .command import CreateEbookCommand, EditEbookCommand, DeleteEbookCommand
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def ebook_list(request):
    return Response({"message": "ebook_list"})
    # ebooks = Ebook.objects.all()
    # return render(request, 'ebook_list.html', {'ebooks': ebooks})

@api_view(['GET'])
def ebook_detail(request, ebook_id): # related to ShowBooksCommand
    return Response({"message": "ebook_detail"})
    # ebook = get_object_or_404(Ebook, pk=ebook_id)
    # return render(request, 'ebook_detail.html', {'ebook': ebook})

@api_view(['GET'])
def create_ebook(request):
    return Response({"message": "Create ebook"})
    # if request.method == 'POST':
    #     form = EbookForm(request.POST)
    #     if form.is_valid():
    #         data = form.cleaned_data
    #         command = CreateEbookCommand(data)
    #         command.execute()
    #         return JsonResponse({'success': True})
    # else:
    #     form = EbookForm()
    # return render(request, 'create_ebook.html', {'form': form})

@api_view(['GET'])
def edit_ebook(request, ebook_id):
    return Response({"message": "edit ebook"})
    # ebook = get_object_or_404(Ebook, pk=ebook_id)
    # if request.method == 'POST':
    #     form = EbookForm(request.POST, instance=ebook)
    #     if form.is_valid():
    #         data = form.cleaned_data
    #         command = UpdateEbookCommand(ebook_id, data)
    #         command.execute()
    #         return JsonResponse({'success': True})
    # else:
    #     form = EbookForm(instance=ebook)
    # return render(request, 'update_ebook.html', {'form': form, 'ebook': ebook})

@api_view(['GET'])
def delete_ebook(request, ebook_id):
    return Response({"message": "delete ebook"})
    # ebook = get_object_or_404(Ebook, pk=ebook_id)
    # if request.method == 'POST':
    #     command = DeleteEbookCommand(ebook_id)
    #     command.execute()
    #     return JsonResponse({'success': True})
    # return render(request, 'delete_ebook.html', {'ebook': ebook})
