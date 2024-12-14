from datetime import timedelta

from django.http import JsonResponse, FileResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from api.generics import BaseAPIView, BaseView
from api.service import RobotService, CustomerService, OrderService


class CreateRobotView(BaseAPIView):

    def post(self, request, *args, **kwargs):
        try:
            data = self.get_data_json()
            RobotService.validate_robot_data(data)
            robot = RobotService.create_robot(
                model=data['model'],
                version=data['version'],
                created=parse_datetime(data['created']),
            )
            return JsonResponse({'robot_id': robot.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class RobotStatsView(BaseView):

    def get(self, request, *args, **kwargs):
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        file = RobotService.get_stats_file(start_date, end_date)
        return FileResponse(file, filename=f'robots.xlsx')


class RobotOrderView(BaseAPIView):

    def post(self, request, *args, **kwargs):
        try:
            data = self.get_data_json()
            customer = CustomerService.get_customer(data['customer_email'])
            robot_serial = data['robot_serial']
            order = OrderService.create_order(customer, robot_serial)
            return JsonResponse({'status': order.status}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
