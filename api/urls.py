from django.urls import path
from search.views import direct_search,InDirect_search
from eBook.views import ebook_list,ebook_detail,delete_ebook,create_ebook,edit_ebook
urlpatterns = [
    path('ebook_list/', ebook_list),
    path('ebook_detail/', ebook_detail),
    path('delete_ebook/', delete_ebook),
    path('create_ebook/', create_ebook),
    path('edit_ebook/', edit_ebook),
    path('direct_search/', direct_search),
    path('InDirect_search/', InDirect_search),
]