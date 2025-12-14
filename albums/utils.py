import json
from pathlib import Path
from django.conf import settings
from .models import Album

EXPORT_PATH = Path(settings.MEDIA_ROOT) / 'exports' / 'albums.json'
EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

def parse_json_file():
    if not EXPORT_PATH.exists():
        return []
    try:
        with open(EXPORT_PATH, 'r', encoding='utf8') as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def write_json_file(items):
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EXPORT_PATH, 'w', encoding='utf8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def save_as_json(album):
    items = parse_json_file()
    items.append(album)
    write_json_file(items)

def is_duplicate_in_db(album, exclude_id=None):
    qs = Album.objects.filter(
        title__iexact=album['title'],
        artist__iexact=album['artist'],
        year=album['year'],
        genre__iexact=album.get('genre', ''),
        tracks=album['tracks'],
        country__iexact=album.get('country', ''),
    )
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()

def is_duplicate_in_json(album, exclude_index=None):
    items = parse_json_file()
    for idx, it in enumerate(items):
        if exclude_index is not None and exclude_index == idx:
            continue
        try:
            if (
                it.get('title', '').strip().lower() == album['title'].strip().lower()
                and it.get('artist', '').strip().lower() == album['artist'].strip().lower()
                and int(it.get('year', 0)) == album['year']
            ):
                return True
        except Exception:
            continue
    return False
