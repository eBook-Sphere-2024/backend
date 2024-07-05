from abc import ABC, abstractmethod
from django.shortcuts import get_object_or_404
from User.serializers import RegisterSerializer
from .models import eBook , Category
from eBook.serializers import RatingSerializer, eBookSerializer , CategorySerializer
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import send_mail
from eBook.utility import *
from search.semanticSearch import semanticSearch
from eBook.utility import *
semantic_search_instance = semanticSearch()

# Base Command class
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

# Concrete command classes
class CreateEbookCommand(Command):
    def __init__(self, data):
        self.data = data

    def execute(self):
        serializer = eBookSerializer(data=self.data)
        if serializer.is_valid():
           serializer.save()  # Save the eBook instance
           return serializer.data
        return serializer.errors


class EditEbookCommand(Command):
    def __init__(self, ebook_id, data):
        self.ebook_id = ebook_id
        self.data = data

    def execute(self):
        try:
            ebook = eBook.objects.get(id=self.ebook_id)
            serializer = eBookSerializer(ebook, data=self.data, partial=True)
            if serializer.is_valid():
                if 'is_reviewed' not in self.data:
                    serializer.save()
                elif serializer.validated_data.get('is_reviewed')==True and not ebook.is_reviewed:
                    try:
                        folderIdToMoveTo = '17iMoJjzjuOvF0giYCGZjfLZuoD5hp5NI'
                        folderIdToMoveToCover='155RIatX8R6Abd_6UQDpJe5wirqRRU1E3'
                        fileId = move_file_in_google_drive(ebook.content ,folderIdToMoveTo)
                        start_index = ebook.cover.find('id=') + len("id=")
                        cover = ebook.cover[start_index:]
                        coverId = moveCoverInGoogleDrive(cover ,folderIdToMoveToCover)
                        ebook.content = fileId 
                        ebook.cover = "https://drive.google.com/thumbnail?id="+ coverId
                        serializer.save()
                        #add indexing
                        try:
                            semantic_search_instance.index_one_ebook(fileId)
                        except:
                            return False,"Error in indexing file", serializer.errors
                        #email confirm
                        subject = 'Response of Ebook Review'
                        message = render_to_string('ReviewEmails/reviewAccepted.txt', {
                            'Author': ebook.author.username,
                            'Title': ebook.title
                        })
                        send_mail(subject, message, 'ebooksphere210@gmail.com', [ebook.author.email])
                    except:
                        return False,"Error in moving file", serializer.errors
                elif serializer.validated_data.get('is_reviewed')==True and ebook.is_reviewed:
                    serializer.save()
                elif serializer.validated_data.get('is_reviewed')==False and not ebook.is_reviewed:
                    serializer.save()
                    #remove from drive and from ebooks table
                    try:
                        delete_file_in_google_drive(ebook.content)
                    except:
                        return False,"Error in deleting file", serializer.errors
                    try:
                        start_index = ebook.cover.find('id=') + len('id=')
                        cover = ebook.cover[start_index:]
                        delete_file_in_google_drive(cover)
                    except:
                        return False,"Error in deleting cover", serializer.errors
                    eBook.objects.filter(id=ebook.id).delete()

                    subject = 'Response of Ebook Review'
                    message = render_to_string('ReviewEmails/reviewRejected.txt', {
                        'Author': ebook.author.username,
                        'Title': ebook.title
                    })
                    send_mail(subject, message, 'ebooksphere210@gmail.com', [ebook.author.email])
                else:
                    serializer.save()
                return True,"Success", serializer.data
            else:
                return False,"Error", serializer.errors
        except ObjectDoesNotExist:
            return False,"eBook not found", None

class DeleteEbookCommand(Command):
    def __init__(self, ebook_id):
        self.ebook_id = ebook_id

    def execute(self):
        ebook = eBook.objects.get(id=self.ebook_id)
        delete_file_in_google_drive(ebook.content)
        start_index = ebook.cover.find('id=') + len('id=')
        cover = ebook.cover[start_index:]
        delete_file_in_google_drive(cover)
        if(ebook.is_reviewed == True):
            semantic_search_instance.delete_document_by_fileid(ebook.content)
        eBook.objects.filter(id=self.ebook_id).delete()

class ShowBooksCommand(Command):
    def execute(self):
        ebooks = eBook.objects.filter(is_reviewed=True)
        serialized_ebooks = []
        for ebook in ebooks:
            author_instance = ebook.author
            categories = ebook.categories.all()
            serialized_ebook = eBookSerializer(ebook).data
            serialized_ebook['categories'] = CategorySerializer(categories, many=True).data
            serialized_ebook['author'] = RegisterSerializer(author_instance).data
            serialized_ebooks.append(serialized_ebook)
        return serialized_ebooks
    
class ShowEbookDetailsCommand(Command):
    def __init__(self, ebook_id):
        self.ebook_id = ebook_id

    def execute(self):
        ebook = get_object_or_404(eBook, id=self.ebook_id)
        if(ebook.is_reviewed == False):
            return None
        categories = ebook.categories.all()
        serializer = eBookSerializer(ebook)
        serialized_data = serializer.data
        serialized_data['categories'] = CategorySerializer(categories, many=True).data
        serialized_data['author'] = RegisterSerializer(ebook.author).data
        return serialized_data
    
class FilterBooksByCategoryCommand(Command):
    def __init__(self, category_id):
        self.category_id = category_id

    def execute(self):
        eBooks=eBook.objects.filter(is_reviewed=True)
        return eBooks.filter(categories__id=self.category_id ) 

    
class ShowCategoriesCommand(Command):
    def execute(self):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return serializer.data

