from django.urls import path
from search.views import direct_search,InDirect_search
from eBook.views import *
urlpatterns = [
    path('ebooks/', EbookAPI.as_view()),
    path('ebook_categories/', EbookCategoryAPI.as_view()),
    path('filter/', filter_books_by_category),
    path('direct_search/', direct_search),
    path('InDirect_search/', InDirect_search),
]