from django.db import models

from customers.models import Customer


class Order(models.Model):
    class Status(models.TextChoices):
        WAITING = 'waiting', 'В ожидании'
        COMPLETED = 'completed', 'Завершен'  # Мб название нужно поменять

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    robot = models.OneToOneField('robots.Robot', on_delete=models.SET_NULL, null=True, related_name='order')
    robot_serial = models.CharField(max_length=5, blank=False, null=False)
    status = models.CharField(max_length=20, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
