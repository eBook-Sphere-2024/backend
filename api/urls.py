from django.urls import path
from Comments.views import CommentAPI
from eBook.views import *
from User.views import LoginAPI, UserAPI
from search.views import searchAPI , RelatedEBookAPI , IndexAPIView
urlpatterns = [
    path('users/', UserAPI.as_view()),
    path('login/', LoginAPI.as_view()),
    path('ebooks/', EbookAPI.as_view()),
    path('ebook_categories/', EbookCategoryAPI.as_view()),
    path('filter/', filter_books_by_category),
    path('search/',searchAPI.as_view()),
    path('related/',RelatedEBookAPI.as_view()),
    path('index/',IndexAPIView.as_view()),
    path('comments/',CommentAPI.as_view()),
]