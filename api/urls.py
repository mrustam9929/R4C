from django.urls import path

from api import views

urlpatterns = [
    path('robots/', views.CreateRobotView.as_view(), name='create-robots'),
]
