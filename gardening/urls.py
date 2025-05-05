from django.urls import path

from gardening import views

urlpatterns = [
    path('', views.index, name='index'),
]
