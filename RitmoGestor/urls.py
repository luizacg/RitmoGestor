from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('data.urls')),
    path('data/', include('data.urls')),
#    path('api/', include('apis.urls')),
    path('accounts/login/',
          auth_views.LoginView.as_view(template_name='data/login.html'), name='login'),
    path('accounts/logout/',
          auth_views.LogoutView.as_view(template_name='data/logout.html'), name='logout'),
]
