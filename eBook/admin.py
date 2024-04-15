from django.contrib import admin
from .models import eBook, Category

class eBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_date')
    list_filter = ('publication_date',)
    search_fields = ('title', 'author')
    filter_horizontal = ('categories',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register your models and their custom admin classes
admin.site.register(eBook, eBookAdmin)
admin.site.register(Category, CategoryAdmin)
