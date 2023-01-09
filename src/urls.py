from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from core import views as core_views

urlpatterns = [
    path('', include('pg.urls')),
    #path("super-manager/", admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
