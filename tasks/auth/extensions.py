from drf_spectacular.extensions import OpenApiAuthenticationExtension

class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'authentication.auth.CookieJWTAuthentication'
    name = 'JWTCookieAuth'
    
    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'access_token',
            'description': 'Cookie-based JWT Authentication'
        }