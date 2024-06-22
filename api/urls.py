from django.urls import path
from Comments.views import *
from ReaderAnalysis.views import *
from eBook.views import *
from User.views import *
from Template.views import *
from FavoriteBooks.views import * 
from search.views import searchAPI , RelatedEBookAPI , IndexAPIView , indexAll, deleteIndex
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
    path('template/',TemplateAPI.as_view()),
    path('getTemplateById/',getTemplateById.as_view()),
    path('profile/',User_Profile.as_view()),
    path('autherBooks/',AuthorBooksAPI.as_view()),
    path('replies/',get_all_replies),
    path('autherBooks/',AuthorBooksAPI.as_view()),
    path('download/',download_file_from_google_drive),
    path('userByToken/', get_User_by_Token),
    path('rate/',RatingBooksAPI.as_view()),
    path('changePassword/',ChangePasswordAPI.as_view()),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('FavoriteBooks/',FavoriteBooksAPI.as_view()),
    path('publish/',publish),
    path('ebookContent/',get_ebook_content),
    path('ReaderAnalysis/',ReaderAnalysisAPI.as_view()),
    path('SpecificReaderAnalysis/',SpecificReaderAnalysis),
    path('ReaderAnalysisSpecificBook/',ReaderAnalysisSpecificBook),
    path('CommentAnalysis/',CommentAnalysis),
    path('BookAnalyticsNumbers/',GetBookAnalyticsNumbers),
    path('indexAll/',indexAll),
    path('deleteIndex/',deleteIndex),
    path('contact/',ContactMail),
]