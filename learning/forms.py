from django import forms

class LessonSearchForm(forms.Form):
    q = forms.CharField(required=False, label="Поиск", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Поиск по названию/описанию…"
    }))
    sort = forms.ChoiceField(required=False, label="Сортировка", choices=[
        ("order", "По порядку"),
        ("title", "По названию"),
        ("updated", "По обновлению"),
    ], widget=forms.Select(attrs={"class": "form-select"}))
