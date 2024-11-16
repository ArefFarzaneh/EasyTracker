
from django.contrib import admin
from django.urls import path, include
from chartjs import views 

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('EasyTracker.urls')),

]
