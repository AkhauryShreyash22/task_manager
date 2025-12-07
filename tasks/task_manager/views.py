from django.shortcuts import render

# Create your views here.
# task_manager/views.py

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Task
from .serializers import TaskSerializer
from .permissions import IsAdminOrReadOnly
from auth.auth import CookieJWTAuthentication   



class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"



class TaskListCreateAPI(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["completed"]   

    @extend_schema(
        parameters=[
            OpenApiParameter("completed", bool, OpenApiParameter.QUERY,
                             description="Filter by completion status (true/false)"),
            OpenApiParameter("page", int, OpenApiParameter.QUERY,
                             description="Page number"),
        ],
        responses={200: TaskSerializer(many=True)},
        description="List all tasks (paginated & filterable)"
    )
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        paginator = TaskPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = TaskSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        request=TaskSerializer,
        responses={201: TaskSerializer},
        description="Create a new task"
    )
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



class TaskDetailAPI(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    lookup_field = "pk"

    def get_object(self):
        try:
            return Task.objects.get(pk=self.kwargs["pk"])
        except Task.DoesNotExist:
            return None

    @extend_schema(
        responses={200: TaskSerializer, 404: OpenApiResponse(description="Task not found")},
        description="Retrieve details of a specific task"
    )
    def get(self, request, pk):
        task = self.get_object()
        if not task:
            return Response({"error": "Task not found"}, status=404)
        return Response(TaskSerializer(task).data)

    @extend_schema(
        request=TaskSerializer,
        responses={200: TaskSerializer, 403: OpenApiResponse(description="Forbidden")},
        description="Update a task (admin only)"
    )
    def put(self, request, pk):
        task = self.get_object()
        if not task:
            return Response({"error": "Task not found"}, status=404)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    @extend_schema(
        responses={204: OpenApiResponse(description="Task deleted"), 404: OpenApiResponse(description="Task not found")},
        description="Delete a task (admin only)"
    )
    def delete(self, request, pk):
        task = self.get_object()
        if not task:
            return Response({"error": "Task not found"}, status=404)

        task.delete()
        return Response(status=204)
