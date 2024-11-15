from django.urls import path
from yt_app import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name="index"),
    path('getvideo/', views.getVideo, name='getVideo'),
    path('download/', views.downloadVid, name='downloadVid'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
