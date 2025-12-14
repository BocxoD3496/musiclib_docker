from django.contrib import admin
from .models import Album
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title','artist','year','tracks','country')
    search_fields = ('title','artist','genre','country')
