from django.db.models.deletion import ProtectedError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from src.base.exceptions import BusinessLogicException


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if isinstance(exc, ProtectedError):
        data = ProtectedErrorhandler.handle_exception(exc, context)
        return Response(data=data, status=400)

    if isinstance(exc, BusinessLogicException):
        return Response(
            data={'detail': exc.detail, 'code': exc.code},
            status=exc.status_code
        )
    return response


class ProtectedErrorhandler:

    @staticmethod
    def handle_exception(exc, context):
        protected_objs = exc.protected_objects
        return {
            "error": "У этого объекта есть связи с другими объектами",
            'code': 610,
            'related_objects': [
                {
                    'id': obj.id,
                    'name': obj.__str__(),
                } for obj in protected_objs
            ]
        }
