from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

from api.generics import BaseAPIView, BaseView
from api.service import RobotService
from robots.models import Robot


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
