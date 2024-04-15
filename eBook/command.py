from abc import ABC, abstractmethod
from .models import eBook

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
        eBook.objects.create(**self.data)

class EditEbookCommand(Command):
    def __init__(self, ebook_id, data):
        self.ebook_id = ebook_id
        self.data = data

    def execute(self):
        ebook = eBook.objects.get(id=self.ebook_id)
        for key, value in self.data.items():
            setattr(ebook, key, value)
        ebook.save()

class DeleteEbookCommand(Command):
    def __init__(self, ebook_id):
        self.ebook_id = ebook_id

    def execute(self):
        eBook.objects.filter(id=self.ebook_id).delete()

class ShowBooksCommand(Command):
    def execute(self):
        return eBook.objects.all()
    
class FilterBooksByCategoryCommand(Command):
    def __init__(self, category):
        self.category = category

    def execute(self):
        return eBook.objects.filter(category=self.category)
    
class ShowCategoriesCommand(Command):
    def execute(self):
        return eBook.objects.values_list('category', flat=True).distinct()

