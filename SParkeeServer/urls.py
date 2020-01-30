from django.contrib import admin
from django.urls import include, path
from sparkee_web.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('web/', include('sparkee_web.urls')),
    path('api/', include('sparkee_api.urls')),
]
