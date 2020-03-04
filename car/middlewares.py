from django.utils.deprecation import MiddlewareMixin


class MiddlewareHead(MiddlewareMixin):

    @staticmethod
    def process_response(request, response):
        if request:
            response['Access-Control-Allow-Origin'] = '*'
        return response
