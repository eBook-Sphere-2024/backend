from abc import ABC, abstractmethod
from django.shortcuts import get_object_or_404
from User.serializers import RegisterSerializer
from .models import eBook , Category
from eBook.serializers import RatingSerializer, eBookSerializer , CategorySerializer
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import send_mail
from eBook.utility import *

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
            ebook_instance = serializer.save()  # Save the eBook instance
            
            # Create initial rating for the eBook
            rate_data = {
                'ebook': ebook_instance.id,
                'user': self.data.get('author'),
                'rate': 0
            }
            rating_serializer = RatingSerializer(data=rate_data)
            if rating_serializer.is_valid():
                rating_serializer.save()
                return serializer.data
            else:
                # If creating the initial rating fails, delete the eBook instance
                ebook_instance.delete()
                return rating_serializer.errors
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
                if serializer.validated_data.get('is_reviewed', True) and not ebook.is_reviewed:
                    try:
                        folderIdToMoveTo = '17iMoJjzjuOvF0giYCGZjfLZuoD5hp5NI'
                        folderIdToMoveToCover='155RIatX8R6Abd_6UQDpJe5wirqRRU1E3'
                        fileId = move_file_in_google_drive(ebook.content ,folderIdToMoveTo)
                        coverId = moveCoverInGoogleDrive(ebook.cover ,folderIdToMoveToCover)
                        ebook.content = fileId 
                        ebook.cover = coverId
                        serializer.save()
                        #add indexing
                        subject = 'Response of Ebook Review'
                        message = render_to_string('ReviewEmails/reviewAccepted.txt', {
                            'Author': ebook.author.username,
                            'Title': ebook.title
                        })
                        send_mail(subject, message, 'ebooksphere210@gmail.com', [ebook.author.email])
                    except:
                        return False,"Error in moving file", serializer.errors
                elif serializer.validated_data.get('is_reviewed', True) and ebook.is_reviewed:
                    serializer.save()
                else:
                    serializer.save()
                    #remove from drive and from ebooks table
                    delete_file_in_google_drive(ebook.content)
                    delete_file_in_google_drive(ebook.cover)
                    DeleteEbookCommand(ebook.id).execute()

                    subject = 'Response of Ebook Review'
                    message = render_to_string('ReviewEmails/reviewRejected.txt', {
                        'Author': ebook.author.username,
                        'Title': ebook.title
                    })
                    send_mail(subject, message, 'ebooksphere210@gmail.com', [ebook.author.email])

                return True,"Success", serializer.data
            else:
                return False,"Error", serializer.errors
        except ObjectDoesNotExist:
            return False,"eBook not found", None

class DeleteEbookCommand(Command):
    def __init__(self, ebook_id):
        self.ebook_id = ebook_id

    def execute(self):
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

