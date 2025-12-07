from django.shortcuts import render
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import status
from .utils import set_tokens_cookies, delete_tokens_cookies
from rest_framework.generics import GenericAPIView

from .auth import CookieJWTAuthentication

# Import all serializers
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    LogoutSerializer,
    LoginResponseSerializer,
    RegisterResponseSerializer,
    LogoutResponseSerializer,
    RefreshTokenResponseSerializer,
    ProfileResponseSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(GenericAPIView):
    authentication_classes = []   
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                'Register Example',
                value={
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@example.com",
                    "password": "Password123",
                    "confirm_password": "Password123"
                },
                request_only=True
            ),
            OpenApiExample(
                'Register Success Response',
                value={
                    "message": "User registered successfully",
                    "user": {
                        "id": 1,
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe"
                    }
                },
                response_only=True
            )
        ],
        auth=[]  
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            }
            
            response = Response(response_data, status=status.HTTP_201_CREATED)
            
            response = set_tokens_cookies(
                response, 
                str(refresh.access_token), 
                str(refresh)
            )
            
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPI(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Invalid credentials"),
        },
        examples=[
            OpenApiExample(
                'Login Example',
                value={
                    "email": "john@example.com",
                    "password": "Password123"
                },
                request_only=True
            ),
            OpenApiExample(
                'Login Success Response',
                value={
                    "message": "Login successful",
                    "user": {
                        "id": 1,
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe"
                    }
                },
                response_only=True
            )
        ],
        auth=[]  
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        
        response_data = {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        
        response = set_tokens_cookies(
            response, 
            str(refresh.access_token), 
            str(refresh)
        )
        
        return response


@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication, JWTAuthentication]  # Both for fallback
    serializer_class = LogoutSerializer

    @extend_schema(
        request=LogoutSerializer,
        responses={
            200: LogoutResponseSerializer,
            400: OpenApiResponse(description="Invalid token"),
            401: OpenApiResponse(description="Unauthorized"),
        },
        examples=[
            OpenApiExample(
                'Logout Success Response',
                value={
                    "message": "Logged out successfully"
                },
                response_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except TokenError:
                    pass
            
            response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
            
            # Delete cookies
            response = delete_tokens_cookies(response)
            
            return response
            
        except Exception as e:
            response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
            response = delete_tokens_cookies(response)
            return response


@method_decorator(csrf_exempt, name='dispatch')
class RefreshTokenAPI(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LogoutSerializer

    @extend_schema(
        request=LogoutSerializer,
        responses={
            200: RefreshTokenResponseSerializer,
            400: OpenApiResponse(description="Invalid token"),
        },
        examples=[
            OpenApiExample(
                'Refresh Token Success Response',
                value={
                    "message": "Token refreshed successfully"
                },
                response_only=True
            )
        ],
        auth=[]  
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            if not refresh_token:
                return Response({"error": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            
            response = Response({
                "message": "Token refreshed successfully"
            }, status=status.HTTP_200_OK)
            
            response = set_tokens_cookies(
                response, 
                str(token.access_token), 
                str(token)
            )
            
            return response
            
        except TokenError as e:
            response = Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            response = delete_tokens_cookies(response)
            return response


@method_decorator(csrf_exempt, name='dispatch')
class ProfileAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication, JWTAuthentication] 
    serializer_class = None

    @extend_schema(
        responses={
            200: ProfileResponseSerializer,
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="User details not found"),
        },
        examples=[
            OpenApiExample(
                'Profile Success Response',
                value={
                    "user": {
                        "id": 1,
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe"
                    }
                },
                response_only=True
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            return Response({
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "User details not found"
            }, status=status.HTTP_404_NOT_FOUND)