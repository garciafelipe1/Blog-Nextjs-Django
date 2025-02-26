
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings






urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/media/',include('apps.media.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/blog/', include('apps.blog.urls')),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
