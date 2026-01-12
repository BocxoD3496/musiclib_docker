from learning.admin_site import admin_site
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/report-export/", include("learning.admin_urls")),
    path("admin/", admin_site.urls),

    # Auth + main UI
    path("accounts/", include("accounts.urls")),
    path("", include("learning.urls")),

    # Optional REST API
    path("api/", include("learning.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
