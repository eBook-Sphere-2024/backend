from django.urls import path
from eBook.views import *
from search.views import searchAPI , related_eBook_API , IndexAPIView
urlpatterns = [
    path('ebooks/', EbookAPI.as_view()),
    path('ebook_categories/', EbookCategoryAPI.as_view()),
    path('filter/', filter_books_by_category),
    path('search/',searchAPI.as_view()),
    path('related/',related_eBook_API.as_view()),
    path('index/',IndexAPIView.as_view())
]