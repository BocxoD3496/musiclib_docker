from __future__ import annotations

from typing import Dict, List, Tuple

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.text import slugify

from openpyxl import Workbook

from .models import Language, Lesson, Card, UserLessonProgress, CardReview

MODEL_REGISTRY = {
    "Language": Language,
    "Lesson": Lesson,
    "Card": Card,
    "UserLessonProgress": UserLessonProgress,
    "CardReview": CardReview,
}

def _model_field_choices(model) -> List[Tuple[str, str]]:
    """Return a list of (field_name, verbose_name) for checkboxes."""
    choices = []
    for f in model._meta.get_fields():
        # Skip reverse relations and m2m to keep export simple and safe
        if f.auto_created and not f.concrete:
            continue
        if f.many_to_many:
            continue
        # For FK fields, export the raw id and also a readable string by Django's __str__
        # We'll just export the FK id for simplicity.
        if hasattr(f, "attname"):
            choices.append((f.attname, getattr(f, "verbose_name", f.name)))
    return choices

@staff_member_required
def export_report(request: HttpRequest) -> HttpResponse:
    """Admin-only XLSX export with selection of tables and fields.

    - User chooses one or more models (tables)
    - For each chosen model, selects fields
    - Output: workbook with one sheet per model
    """
    model_fields: Dict[str, List[Tuple[str, str]]] = {name: _model_field_choices(model) for name, model in MODEL_REGISTRY.items()}

    if request.method == "POST":
        selected_models = request.POST.getlist("models")
        # Build selections per model
        selections: Dict[str, List[str]] = {}
        for name in selected_models:
            fields = request.POST.getlist(f"fields__{name}")
            fields = [f for f in fields if any(f == c[0] for c in model_fields.get(name, []))]
            if fields:
                selections[name] = fields

        if not selections:
            messages.error(request, "Выберите хотя бы одну таблицу и хотя бы одно поле.")
            return render(request, "admin/report_export.html", {"model_fields": model_fields})

        wb = Workbook()
        # Remove default sheet
        default_ws = wb.active
        wb.remove(default_ws)

        for model_name, fields in selections.items():
            Model = MODEL_REGISTRY[model_name]
            qs = Model.objects.all()

            # Sheet title max length = 31
            title = model_name[:31]
            ws = wb.create_sheet(title=title)

            # Header
            ws.append(fields)

            for obj in qs.iterator():
                row = []
                for field in fields:
                    val = getattr(obj, field, "")
                    # Convert datetimes to naive string for spreadsheet readability
                    if val is None:
                        row.append("")
                    else:
                        row.append(str(val))
                ws.append(row)

            # Make header bold-ish by increasing row height (simple visual touch)
            ws.row_dimensions[1].height = 18

        from io import BytesIO
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)

        filename = "langstudy_export.xlsx"
        response = HttpResponse(
            buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    return render(request, "admin/report_export.html", {"model_fields": model_fields})
