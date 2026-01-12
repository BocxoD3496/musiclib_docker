from django.contrib.admin import AdminSite
from django.urls import reverse


class CustomAdminSite(AdminSite):
    site_header = "LangStudy — Администрирование"
    site_title = "LangStudy Admin"
    index_title = "Панель управления"

    def each_context(self, request):
        context = super().each_context(request)
        context["report_export_url"] = reverse("admin_report_export")
        return context


admin_site = CustomAdminSite(name="custom_admin")
