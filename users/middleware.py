class JWTAuthtenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'access_token' in request.session:
            request.META['HTTP_AUTHORIZATION'] = f"Bearer {request.session['access_token']}"
        response = self.get_response(request)
        return response