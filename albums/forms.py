from django import forms
from .models import Album

DEST_CHOICES = [
    ('json', 'Сохранить в JSON'),
    ('db', 'Сохранить в базу данных'),
]

class AlbumForm(forms.ModelForm):
    destination = forms.ChoiceField(
        choices=DEST_CHOICES,
        widget=forms.RadioSelect,
        initial='json',
        label='Куда сохранять',
    )

    class Meta:
        model = Album
        fields = ['title', 'artist', 'year', 'genre', 'tracks', 'country']

    def clean_year(self):
        y = self.cleaned_data['year']
        if y < 1800 or y > 2100:
            raise forms.ValidationError('Год должен быть 1800–2100')
        return y

    def clean_tracks(self):
        t = self.cleaned_data['tracks']
        if t < 0 or t > 1000:
            raise forms.ValidationError('Некорректное число треков')
        return t

class JSONUploadForm(forms.Form):
    json_file = forms.FileField(label='JSON файл')
