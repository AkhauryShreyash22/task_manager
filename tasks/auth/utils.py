from rest_framework.response import Response

def set_tokens_cookies(response, access_token, refresh_token):
    """Set JWT tokens as HTTP-only cookies"""
    response.set_cookie(
        key='access_token',
        value=access_token,
        max_age=60 * 60 * 24,  
        secure=False,
        httponly=True,
        samesite='Lax',
        path='/',
    )
    
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        max_age=60 * 60 * 24 * 7,  
        secure=False,
        httponly=True,
        samesite='Lax',
        path='/',
    )
    
    return response

def delete_tokens_cookies(response):
    """Delete JWT tokens cookies on logout"""
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response