from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            if hasattr(exc, 'detail'):
                if isinstance(exc.detail, dict):
                    errors = {}
                    for field, error_list in exc.detail.items():
                        if isinstance(error_list, list):
                            errors[field] = error_list[0] if error_list else "Invalid value"
                        else:
                            errors[field] = str(error_list)
                    return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
                elif isinstance(exc.detail, list):
                    return Response({"errors": {"non_field_errors": exc.detail}}, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, Exception):
        return Response({
            "error": "An unexpected error occurred",
            "detail": str(exc)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response