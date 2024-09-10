from django.urls import path
from predicion import views

urlpatterns = [
    path('',views.index)
]
