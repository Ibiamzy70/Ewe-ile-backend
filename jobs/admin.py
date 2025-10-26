from django.contrib import admin
from .models import Job, JobApplication, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "owner",
        "employment_level",
        "job_type",
        "pay_type",
        "currency",
        "is_published",
        "is_verified",
        "created_at",
    )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = (
        "title",
        "company",
        "description",
        "location",
        "skills",
        "qualifications",
    )
    list_filter = (
        "employment_level",
        "job_type",
        "pay_type",
        "location_type",
        "remote_allowed",
        "is_published",
        "is_verified",
        "category",
        "currency",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("owner", "category")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "slug")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "job",
        "email",
        "first_name",
        "last_name",
        "experience_level",
        "reviewed",
        "shortlisted",
        "hired",
        "created_at",
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone",
        "skills",
        "job__title",
        "job__company",
    )
    list_filter = (
        "experience_level",
        "reviewed",
        "shortlisted",
        "hired",
        "created_at",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("job", "applicant", "reviewer")
    readonly_fields = ("created_at", "reviewed_at")

