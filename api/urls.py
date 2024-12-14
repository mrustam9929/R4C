from django.urls import path

from api import views

urlpatterns = [
    path('robots-stats/', views.RobotStatsView.as_view(), name='robots-stats'),
    path('robots/order/', views.RobotOrderView.as_view(), name='order-robots'),
    path('robots/', views.CreateRobotView.as_view(), name='create-robots'),

]
