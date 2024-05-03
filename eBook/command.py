from abc import ABC, abstractmethod
from django.shortcuts import get_object_or_404
from User.serializers import RegisterSerializer
from Template.serializers import TemplateSerializer
from .models import eBook , Category
from eBook.serializers import eBookSerializer , CategorySerializer
from django.core.exceptions import ObjectDoesNotExist

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
        print(self.data)
        if serializer.is_valid():
            serializer.save()
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
        eBook.objects.filter(id=self.ebook_id).delete()

class ShowBooksCommand(Command):
    def execute(self):
        ebooks = eBook.objects.all()
        serialized_ebooks = []
        for ebook in ebooks:
            author_instance = ebook.author
            template_instance = ebook.template
            categories = ebook.categories.all()
            serialized_ebook = eBookSerializer(ebook).data
            serialized_ebook['categories'] = CategorySerializer(categories, many=True).data
            serialized_ebook['author'] = RegisterSerializer(author_instance).data
            serialized_ebook['template'] = TemplateSerializer(template_instance).data
            serialized_ebooks.append(serialized_ebook)
        return serialized_ebooks
    
class ShowEbookDetailsCommand(Command):
    def __init__(self, ebook_id):
        self.ebook_id = ebook_id

    def execute(self):
        ebook = get_object_or_404(eBook, id=self.ebook_id)
        categories = ebook.categories.all()
        serializer = eBookSerializer(ebook)
        serialized_data = serializer.data
        serialized_data['categories'] = CategorySerializer(categories, many=True).data
        serialized_data['author'] = RegisterSerializer(ebook.author).data
        serialized_data['template'] = TemplateSerializer(ebook.template).data
        return serialized_data
    
class FilterBooksByCategoryCommand(Command):
    def __init__(self, category_id):
        self.category_id = category_id

    def execute(self):
        return eBook.objects.filter(categories__id=self.category_id)

    
class ShowCategoriesCommand(Command):
    def execute(self):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return serializer.data

