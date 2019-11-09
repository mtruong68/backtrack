from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

urlpatterns = [
    path('/', include('django.contrib.auth.urls')),
    path('backtrack/', include('backtrackapp.urls')),
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
