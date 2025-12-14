import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.db import models
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import FileResponse
from pathlib import Path
from django.conf import settings

from .forms import AlbumForm, JSONUploadForm
from .models import Album
from . import utils

EXPORT_DIR = Path(settings.MEDIA_ROOT) / 'exports'
IMPORT_DIR = Path(settings.MEDIA_ROOT) / 'imports'
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
IMPORT_DIR.mkdir(parents=True, exist_ok=True)

@require_http_methods(['GET', 'POST'])
def album_create(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            destination = form.cleaned_data['destination']
            album_data = {
                'title': form.cleaned_data['title'].strip(),
                'artist': form.cleaned_data['artist'].strip(),
                'year': form.cleaned_data['year'],
                'genre': form.cleaned_data.get('genre', '').strip(),
                'tracks': form.cleaned_data['tracks'],
                'country': form.cleaned_data.get('country', '').strip(),
            }
            if destination == 'json':
                if utils.is_duplicate_in_json(album_data):
                    messages.info(request, 'Такая запись уже есть в JSON — дубликат не добавлен.')
                else:
                    utils.save_as_json(album_data)
                    messages.success(request, 'Альбом сохранён в JSON.')
            else:
                if utils.is_duplicate_in_db(album_data):
                    messages.info(request, 'Такая запись уже есть в базе — дубликат не добавлен.')
                else:
                    Album.objects.create(**album_data)
                    messages.success(request, 'Альбом сохранён в базу данных.')
            return redirect('albums:album_create')
    else:
        form = AlbumForm()
    return render(request, 'albums/album_form.html', {'form': form})

def choose_source(request):
    return render(request, 'albums/choose_source.html')

def list_from_files(request):
    albums = utils.parse_json_file()
    return render(request, 'albums/file_output.html', {'albums': albums})

def db_list(request):
    return render(request, 'albums/db_output.html')

@require_http_methods(['GET', 'POST'])
def upload_json(request):
    if request.method == 'POST':
        form = JSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['json_file']
            safe_name = f"import_{Path(f.name).stem}.json"
            dest_path = IMPORT_DIR / safe_name
            try:
                raw = f.read().decode('utf-8')
                data = json.loads(raw)
                if not isinstance(data, list):
                    raise ValueError('Ожидался список альбомов.')
                for item in data:
                    if not isinstance(item, dict):
                        raise ValueError('Каждый элемент должен быть объектом.')
                    for key in ['title', 'artist', 'year']:
                        if key not in item:
                            raise ValueError('В каждой записи должны быть поля title, artist, year.')
            except Exception as e:
                if dest_path.exists():
                    dest_path.unlink()
                messages.error(request, f'Файл не прошёл валидацию: {e}')
                return redirect('albums:upload_json')

            with open(dest_path, 'w', encoding='utf-8') as out:
                json.dump(data, out, ensure_ascii=False, indent=2)

            added_db = skipped_db = 0
            added_json = skipped_json = 0

            for item in data:
                album_data = {
                    'title': str(item.get('title', '')).strip(),
                    'artist': str(item.get('artist', '')).strip(),
                    'year': int(item.get('year', 0)),
                    'genre': str(item.get('genre', '') or '').strip(),
                    'tracks': int(item.get('tracks', 0) or 0),
                    'country': str(item.get('country', '') or '').strip(),
                }
                if not utils.is_duplicate_in_db(album_data):
                    Album.objects.create(**album_data)
                    added_db += 1
                else:
                    skipped_db += 1
                if not utils.is_duplicate_in_json(album_data):
                    utils.save_as_json(album_data)
                    added_json += 1
                else:
                    skipped_json += 1

            messages.success(
                request,
                f'Файл {safe_name} загружен. '
                f'В БД добавлено: {added_db}, дублей: {skipped_db}. '
                f'В JSON добавлено: {added_json}, дублей: {skipped_json}.'
            )
            return redirect('albums:choose')
    else:
        form = JSONUploadForm()
    return render(request, 'albums/upload_json.html', {'form': form})

def download_json(request):
    path = Path(settings.MEDIA_ROOT) / 'exports' / 'albums.json'
    if not path.exists():
        return HttpResponseBadRequest('Файл не найден')
    return FileResponse(open(path, 'rb'), as_attachment=True, filename='albums.json')

@require_http_methods(['GET'])
def db_search_api(request):
    q = request.GET.get('q', '').strip()
    qs = Album.objects.all()
    if q:
        qs = qs.filter(
            models.Q(title__icontains=q) |
            models.Q(artist__icontains=q) |
            models.Q(genre__icontains=q) |
            models.Q(country__icontains=q)
        )
    data = [a.as_dict() for a in qs]
    return JsonResponse({'ok': True, 'results': data})

@require_http_methods(['POST'])
def api_edit_album(request, pk):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('bad json')
    album = get_object_or_404(Album, pk=pk)
    album_data = {
        'title': payload.get('title', '').strip(),
        'artist': payload.get('artist', '').strip(),
        'year': int(payload.get('year', album.year)),
        'genre': payload.get('genre', '').strip(),
        'tracks': int(payload.get('tracks', album.tracks)),
        'country': payload.get('country', '').strip(),
    }
    if album_data['year'] < 1800 or album_data['year'] > 2100:
        return JsonResponse({'ok': False, 'error': 'Год должен быть 1800–2100'})
    if album_data['tracks'] < 0 or album_data['tracks'] > 1000:
        return JsonResponse({'ok': False, 'error': 'Некорректное число треков'})
    if utils.is_duplicate_in_db(album_data, exclude_id=album.pk):
        return JsonResponse({'ok': False, 'error': 'Такая запись уже существует (дубликат).'})

    for field, val in album_data.items():
        setattr(album, field, val)
    album.save()
    return JsonResponse({'ok': True})

@require_http_methods(['POST'])
def api_delete_album(request, pk):
    album = get_object_or_404(Album, pk=pk)
    album.delete()
    return JsonResponse({'ok': True})

@require_http_methods(['GET'])
def json_list_api(request):
    items = utils.parse_json_file()
    return JsonResponse({'ok': True, 'results': items})

@require_http_methods(['POST'])
def api_json_add(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('bad json')
    album_data = {
        'title': data.get('title', '').strip(),
        'artist': data.get('artist', '').strip(),
        'year': int(data.get('year', 0)),
        'genre': data.get('genre', '').strip(),
        'tracks': int(data.get('tracks', 0)),
        'country': data.get('country', '').strip(),
    }
    if utils.is_duplicate_in_json(album_data):
        return JsonResponse({'ok': False, 'error': 'Дубликат в JSON.'})
    utils.save_as_json(album_data)
    return JsonResponse({'ok': True})

@require_http_methods(['POST'])
def api_json_edit(request, idx):
    try:
        idx = int(idx)
        data = json.loads(request.body)
    except Exception:
        return HttpResponseBadRequest('bad request')
    items = utils.parse_json_file()
    if idx < 0 or idx >= len(items):
        return JsonResponse({'ok': False, 'error': 'index out of range'})
    album_data = {
        'title': data.get('title', '').strip(),
        'artist': data.get('artist', '').strip(),
        'year': int(data.get('year', 0)),
        'genre': data.get('genre', '').strip(),
        'tracks': int(data.get('tracks', 0)),
        'country': data.get('country', '').strip(),
    }
    if utils.is_duplicate_in_json(album_data, exclude_index=idx):
        return JsonResponse({'ok': False, 'error': 'Дубликат в JSON.'})
    items[idx] = album_data
    utils.write_json_file(items)
    return JsonResponse({'ok': True})

@require_http_methods(['POST'])
def api_json_delete(request, idx):
    try:
        idx = int(idx)
    except ValueError:
        return HttpResponseBadRequest('bad index')
    items = utils.parse_json_file()
    if idx < 0 or idx >= len(items):
        return JsonResponse({'ok': False, 'error': 'index out of range'})
    items.pop(idx)
    utils.write_json_file(items)
    return JsonResponse({'ok': True})
