from django.urls import path
from .admin_views import export_report

urlpatterns = [
    path("", export_report, name="admin_report_export"),
]
