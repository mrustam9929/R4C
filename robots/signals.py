from django.db.models.signals import post_save
from django.dispatch import receiver

from api.service import OrderService, CustomerService
from robots.models import Robot


@receiver(post_save, sender=Robot)
def check_and_notify_waiting_orders(sender, instance, created, **kwargs):
    """
    Сигнал, который проверяет заказы в статусе 'waiting'
    и отправляет уведомления клиентам при создании нового робота.
    """
    if created:
        waiting_orders = OrderService.get_waiting_orders(instance)
        if waiting_orders.exists():
            CustomerService.notify_customer_robot_available(waiting_orders, instance)
