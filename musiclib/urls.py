from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include(('albums.urls', 'albums'), namespace='albums')),
    path('admin/', admin.site.urls),
]
