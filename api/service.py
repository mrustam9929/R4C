import io
from datetime import datetime

import xlsxwriter
from django.core.mail import send_mail
from django.db.models import Count, QuerySet
from django.utils.dateparse import parse_datetime

from customers.models import Customer
from orders.models import Order
from robots.models import Robot


class RobotService:
    @staticmethod
    def create_robot(model: str, version: str, created: datetime) -> Robot:
        robot = Robot.objects.create(
            model=model,
            version=version,
            serial=Robot.get_robot_serial(model, version),
            created=created
        )
        return robot

    @staticmethod
    def validate_robot_data(data) -> None:
        if not all(key in data for key in ['model', 'version', 'created']):
            raise Exception('Missing fields. Required: model, version, created.')
        try:
            created = parse_datetime(data['created'])
        except ValueError:
            raise Exception('Invalid created date format')

        ### Валидация на повторное создание робота
        is_exists = Robot.objects.filter(
            seria=Robot.get_robot_serial(data['model'], data['version']),
            model=data['model'],
            version=data['version'],
            created=created
        ).exists()

        if is_exists:
            raise Exception('Robot already save')

    @staticmethod
    def get_stats_file(start_date, end_date) -> io.BytesIO:

        robots = Robot.objects.filter(
            created__range=(start_date, end_date)
        ).values('serial', 'model', 'version').annotate(count=Count('id')).order_by('serial')

        data = {}
        for robot in robots:
            if robot['model'] in data:
                data[robot['model']].append(robot)
            else:
                data[robot['model']] = [robot]

        file = io.BytesIO()
        workbook = xlsxwriter.Workbook(
            file,
            options={
                'constant_memory': True  # для оптимизации (ограничивает функционал)
            }
        )

        for model, robots in data.items():
            sheet = workbook.add_worksheet(name=model)
            sheet.write(0, 0, 'Модель')
            sheet.write(0, 1, 'Версия')
            sheet.write(0, 2, 'Количество за неделю')
            for row, robot in enumerate(robots, 1):
                sheet.write(row, 0, robot['model'])
                sheet.write(row, 1, robot['version'])
                sheet.write(row, 3, robot['count'])

        workbook.close()
        file.seek(0)
        return file


class CustomerService:

    @staticmethod
    def get_customer(email: str) -> Customer:
        customer, _ = Customer.objects.get_or_create(email=email)
        return customer

    @staticmethod
    def notify_customer_robot_available(waiting_orders: QuerySet, robot: Robot) -> None:
        # Отправляем письмо каждому клиенту
        recipient_list = [order.customer.email for order in waiting_orders]
        send_mail(  # FIXME нужно указать креды в settings
            subject="Робот доступен для заказа",
            message=(
                f"Добрый день!\n\n"
                f"Недавно вы интересовались нашим роботом модели {robot.model}, версии {robot.version}. "
                f"Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами."
            ),
            from_email="info@robots.com",
            recipient_list=recipient_list,
        )


class OrderService:

    @staticmethod
    def create_order(customer: Customer, robot_serial: str) -> Order:
        robot = Robot.objects.filter(
            serial=robot_serial,
            order__isnull=True
        ).first()
        if robot:
            status = Order.Status.COMPLETED
        else:
            status = Order.Status.WAITING

        order = Order.objects.create(
            customer=customer,
            status=status,
            robot_serial=robot_serial,
            robot=robot
        )
        return order

    @staticmethod
    def get_waiting_orders(robot: Robot):
        return Order.objects.filter(
            robot_serial=robot.serial,
            status=Order.Status.WAITING
        ).select_related('customer')
