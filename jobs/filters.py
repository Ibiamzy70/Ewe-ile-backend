import django_filters
from .models import Job

class JobFilter(django_filters.FilterSet):
    min_salary = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    max_salary = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    location = django_filters.CharFilter(field_name='location', lookup_expr='icontains')
    category = django_filters.NumberFilter(field_name='category__id')
    job_type = django_filters.CharFilter(field_name='job_type', lookup_expr='iexact')
    employment_level = django_filters.CharFilter(field_name='employment_level', lookup_expr='iexact')
    pay_type = django_filters.CharFilter(field_name='pay_type', lookup_expr='iexact')
    remote_allowed = django_filters.BooleanFilter(field_name='remote_allowed')

    class Meta:
        model = Job
        fields = [
            'category',
            'job_type',
            'employment_level',
            'pay_type',
            'remote_allowed',
            'location',
            'min_salary',
            'max_salary',
            'is_published',
            'is_verified',
            'currency',
        ]
