from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        if self._non_loggedin_request(request):
            return None
            
        access_token = request.COOKIES.get('access_token')
        
        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            try:
                return super().authenticate(request)
            except Exception:
                raise AuthenticationFailed(
                    "Your session has expired. Please log in again."
                )
        else:
            raise AuthenticationFailed(
                "You are not logged in. Please log in to access this resource."
            )
    
    def _non_loggedin_request(self, request):
        swagger_paths = [
            '/swagger/',
            '/swagger',
            '/api/schema/',
            '/api/schema',
            '/redoc/',
            '/redoc',
            '/schema',
            '/login'
        ]
        
        path = request.path
        return any(swagger_path in path for swagger_path in swagger_paths)
    