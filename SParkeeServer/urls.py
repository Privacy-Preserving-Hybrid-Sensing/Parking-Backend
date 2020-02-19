from django.contrib import admin
from django.urls import include, path
from web.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('web/', include('web.urls')),
    path('api/', include('api.urls')),
]
