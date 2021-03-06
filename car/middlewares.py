from django.utils.deprecation import MiddlewareMixin


class MiddlewareHead(MiddlewareMixin):

    @staticmethod
    def process_response(request, response):
        if request:
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Headers'] = '*'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['X-Frame-Options'] = '*'
        return response
