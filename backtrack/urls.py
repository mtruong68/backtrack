from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('backtrack/', include('backtrackapp.urls')),
    path('admin/', admin.site.urls),
]