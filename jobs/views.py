from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Job, JobApplication, Category
from .serializers import JobSerializer, JobApplicationSerializer, CategorySerializer
from .permissions import IsOwnerOrAdminOrReadOnly
from .filters import JobFilter


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related("category", "owner").all()
    serializer_class = JobSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = JobFilter
    search_fields = ("title", "description", "company", "location", "skills", "qualifications")
    ordering_fields = ("created_at", "salary_min", "salary_max", "employment_level")
    ordering = ("-created_at",)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def applications(self, request, pk=None):
        job = self.get_object()
        if job.owner != request.user and not request.user.is_staff:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        qs = job.applications.all()
        page = self.paginate_queryset(qs)
        serializer = JobApplicationSerializer(page or qs, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.select_related("job", "applicant", "reviewer").all()
    serializer_class = JobApplicationSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("email", "first_name", "last_name", "phone", "skills", "cover_letter")
    ordering_fields = ("created_at", "experience_level")
    ordering = ("-created_at",)

    def get_permissions(self):
        if self.action == "create":
            return []
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return super().get_queryset()
        if user.is_authenticated:
            return super().get_queryset().filter(job__owner=user)
        return JobApplication.objects.none()

    def perform_update(self, serializer):
        instance = serializer.instance
        reviewed_before = instance.reviewed
        instance = serializer.save()
        if not reviewed_before and instance.reviewed:
            instance.reviewer = self.request.user
            instance.reviewed_at = timezone.now()
            instance.save()



