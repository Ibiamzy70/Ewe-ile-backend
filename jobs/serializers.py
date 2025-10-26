from rest_framework import serializers
from django.utils.text import slugify
from .models import Job, JobApplication, Category



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')
        read_only_fields = ('id', 'slug')

    def create(self, validated_data):
        
        name = validated_data.get('name')
        if name and not validated_data.get('slug'):
            validated_data['slug'] = slugify(name)
        return super().create(validated_data)


class JobSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'description', 'company', 'location',
            'location_type', 'category', 'category_id', 'employment_level',
            'job_type', 'pay_type', 'salary_min', 'salary_max', 'currency',
            'remote_allowed', 'experience_required', 'qualifications', 'skills',
            'is_published', 'is_verified', 'expires_at', 'created_at', 'updated_at',
            'owner', 'owner_id'
        ]
        read_only_fields = (
            'id', 'slug', 'created_at', 'updated_at', 'owner', 'owner_id', 'is_verified'
        )

    def validate(self, data):
        min_salary = data.get('salary_min')
        max_salary = data.get('salary_max')
        if min_salary and max_salary and min_salary > max_salary:
            raise serializers.ValidationError("salary_min cannot be greater than salary_max.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        owner = getattr(request, 'user', None)

        validated_data['owner'] = owner

        
        title = validated_data.get('title')
        if title and not validated_data.get('slug'):
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            validated_data['slug'] = slug

        return super().create(validated_data)

    def update(self, instance, validated_data):
        
        title = validated_data.get('title')
        if title and title != instance.title:
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exclude(id=instance.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            instance.slug = slug
        return super().update(instance, validated_data)



class JobApplicationSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.filter(is_published=True)
    )
    applicant = serializers.StringRelatedField(read_only=True)
    applicant_id = serializers.PrimaryKeyRelatedField(
        source='applicant', read_only=True
    )

    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'applicant', 'applicant_id', 'first_name', 'last_name',
            'email', 'phone', 'cover_letter', 'resume', 'experience_level',
            'skills', 'reviewed', 'reviewed_at', 'reviewer', 'shortlisted',
            'hired', 'created_at'
        ]
        read_only_fields = (
            'id', 'created_at', 'reviewed', 'reviewed_at', 'reviewer',
            'shortlisted', 'hired', 'applicant', 'applicant_id'
        )

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            validated_data['applicant'] = user
            validated_data.setdefault('email', user.email or validated_data.get('email'))
            validated_data.setdefault('first_name', getattr(user, 'first_name', ''))
            validated_data.setdefault('last_name', getattr(user, 'last_name', ''))

        return super().create(validated_data)
