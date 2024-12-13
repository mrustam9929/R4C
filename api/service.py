import io
from datetime import datetime

import xlsxwriter
from django.db.models import Count
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
