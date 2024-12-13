from datetime import datetime, date

from django.utils.dateparse import parse_datetime

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
