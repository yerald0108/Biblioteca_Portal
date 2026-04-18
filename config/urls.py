from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from biblioteca import views as biblioteca_views


from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('',          views.home,     name='home'),
    path('registro/', views.registro, name='registro'),
    path('biblioteca/', include('biblioteca.urls', namespace='biblioteca')),
    path('auth/login/',  auth_views.LoginView.as_view(),  name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)