import json

from django.views.generic import View


class BaseView(View):
    pass


class BaseAPIView(BaseView):  # Такое решение из-за того что нельзя использовать DRF

    def get_data_json(self) -> dict:
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            return data
        except json.JSONDecodeError:
            raise Exception('Invalid JSON')
