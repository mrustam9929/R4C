from django.urls import path

from api import views

urlpatterns = [
    path('robots-stats/', views.RobotStatsView.as_view(), name='robots-stats'),
    path('robots/', views.CreateRobotView.as_view(), name='create-robots'),

]
