class RequestLoggerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Req path", request.path)
        print("Req host", request.get_host())
        print("Req Cookies", request.COOKIES)
        print("Req Headers", request.headers)

        response = self.get_response(request)

        print("Resp headers", response.headers)
        print("Resp cookies", response.cookies)
        print("Resp status", response.status_code)
        return response
