import uuid
import os
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

def exam_upload_path(instance, filename):
    """
    Generates a unique path for uploaded files to prevent filename collisions.
    Structure: uploads/YYYY/MM/DD/uuid.ext
    """
    ext = filename.split('.')[-1]
    filename = f"{instance.id}.{ext}"
    return os.path.join('uploads', '%Y', '%m', '%d', filename)

# --- DEFAULT CONFIGURATIONS ---

def default_grading_scheme():
    """
    Standard CBC Grading (Junior Secondary).
    Can be overridden by the frontend for 8-4-4 or other systems.
    """
    return [
        {"min": 80, "max": 100, "grade": "EE", "remark": "Exceeding Expectations", "points": 4},
        {"min": 50, "max": 79,  "grade": "ME", "remark": "Meeting Expectations",   "points": 3},
        {"min": 40, "max": 49,  "grade": "AE", "remark": "Approaching Expectations", "points": 2},
        {"min": 0,  "max": 39,  "grade": "BE", "remark": "Below Expectations",     "points": 1},
    ]

class ExamUpload(models.Model):
    # 1. Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    # 2. Ownership
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exam_uploads'
    )

    # 3. Basic Info
    title = models.CharField(
        max_length=255, 
        help_text=_("e.g., 'Midterm Exams - Class 8 West - 2024'")
    )

    slug = models.SlugField(
        max_length=255, 
        unique=True, 
        blank=True,
        help_text="Unique URL identifier, auto-generated from title."
    )

    # 4. The File
    file = models.FileField(
        upload_to=exam_upload_path, 
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls', 'csv'])],
        help_text=_("Upload your exam data file here (Excel or CSV only)")
    )

    # 5. CONFIGURATION (The "Brain" of the extraction)
    
    # A. Dynamic Grading
    grading_scheme = models.JSONField(
        default=default_grading_scheme,
        help_text="Custom grading rules (JSON) for this specific exam."
    )

    # B. The "Safety Valve" - New Field!
    custom_ignore_columns = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=_("Comma-separated list of columns to exclude from grading (e.g., 'UPI, Nemis No, Stream').")
    )

    # 6. Status & Results
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        db_index=True 
    )

    message = models.TextField(
        blank=True, 
        null=True, 
        help_text=_("Processing notes or error messages.")
    )

    analysis_summary = models.JSONField(
        default=dict, 
        blank=True, 
        help_text=_("JSON summary of results (avg, pass_rate, etc.)")
    )

    # 7. Outputs
    processed_file = models.FileField(upload_to='results/%Y/%m/%d/', null=True, blank=True)
    subject_chart = models.ImageField(upload_to='charts/%Y/%m/', null=True, blank=True)
    passrate_chart = models.ImageField(upload_to='charts/%Y/%m/', null=True, blank=True)
    reports_zip = models.FileField(upload_to='reports/%Y/%m/%d/', null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _("Exam File Upload")
        verbose_name_plural = _("Exam File Uploads")
        permissions = [
            ("can_process_exam", "Can trigger exam processing"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while ExamUpload.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{num}'
            num += 1
        return unique_slug

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED