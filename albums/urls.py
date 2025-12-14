from django.urls import path
from . import views

app_name = 'albums'

urlpatterns = [
    path('', views.album_create, name='album_create'),
    path('choose/', views.choose_source, name='choose'),
    path('files/', views.list_from_files, name='list_from_files'),
    path('db/', views.db_list, name='db_list'),
    path('upload-json/', views.upload_json, name='upload_json'),
    path('files/download/', views.download_json, name='download_json'),

    path('api/db/search/', views.db_search_api, name='api_search_albums'),
    path('api/db/<int:pk>/edit/', views.api_edit_album, name='api_edit_album'),
    path('api/db/<int:pk>/delete/', views.api_delete_album, name='api_delete_album'),

    path('api/json/list/', views.json_list_api, name='json_list_api'),
    path('api/json/add/', views.api_json_add, name='api_json_add'),
    path('api/json/<int:idx>/edit/', views.api_json_edit, name='api_json_edit'),
    path('api/json/<int:idx>/delete/', views.api_json_delete, name='api_json_delete'),
]
