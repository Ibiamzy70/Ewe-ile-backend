from django.db import models
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL



JOB_TYPE_CHOICES = (
    ("full_time", "Full time"),
    ("part_time", "Part time"),
    ("contract", "Contract"),
    ("temporary", "Temporary"),
    ("internship", "Internship"),
    ("gig", "Gig / One-off"),
)

EMPLOYMENT_LEVEL_CHOICES = (
    ("unskilled", "Unskilled / Manual Labor"),
    ("semi_skilled", "Semi-skilled / Technical Assistant"),
    ("skilled", "Skilled / Trade Professional"),
    ("professional", "Professional / White Collar"),
)

PAY_TYPE_CHOICES = (
    ("hourly", "Hourly"),
    ("daily", "Daily"),
    ("weekly", "Weekly"),
    ("monthly", "Monthly"),
    ("fixed", "Fixed Contract"),
)

LOCATION_TYPE_CHOICES = (
    ("onsite", "On-site"),
    ("remote", "Remote"),
    ("hybrid", "Hybrid"),
)



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name




class Job(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField()

    company = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPE_CHOICES, default="onsite")

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs")

    employment_level = models.CharField(max_length=20, choices=EMPLOYMENT_LEVEL_CHOICES, default="unskilled")
    job_type = models.CharField(max_length=32, choices=JOB_TYPE_CHOICES, default="full_time")

    pay_type = models.CharField(max_length=20, choices=PAY_TYPE_CHOICES, default="monthly")
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default="USD")

    remote_allowed = models.BooleanField(default=False)
    experience_required = models.PositiveIntegerField(null=True, blank=True, help_text="Years of experience required")
    qualifications = models.TextField(blank=True, help_text="Academic or vocational qualifications")
    skills = models.TextField(blank=True, help_text="Comma-separated list of key skills")

    is_published = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["employment_level"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            counter = 1
            slug = base_slug
            while Job.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} @ {self.company or 'Private Employer'}"



class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications"
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)

    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to="resumes/%Y/%m/%d/", null=True, blank=True)

    experience_level = models.CharField(
        max_length=20, choices=EMPLOYMENT_LEVEL_CHOICES, null=True, blank=True
    )
    skills = models.TextField(blank=True, help_text="Comma-separated list of applicant skills")

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_applications"
    )
    shortlisted = models.BooleanField(default=False)
    hired = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Application for {self.job.title} by {self.email}"



