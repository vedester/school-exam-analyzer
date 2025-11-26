from django.db import models

class ExamUpload(models.Model):
    # 1. Status Choices: Professional way to handle states
    STATUS_CHOICES=[
        ('PENDING','Pending'),
        ('PROCESSING','Processing'),
        ('COMPLETED','Completed'),
        ('FAILED','Failed'),
    ]
    #2. TITLE: What is this upload about?
    title=models.CharField(max_length=255, help_text = "e.g., 'Midterm Exams - Class 8 west - 2024'")

    # 3. file: This uploads files to 'media/uploads/2025/...' to keep folders organized
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', help_text="Upload your exam data file here (Excel, CSV, etc.)")
    # 4. uploaded_at: When was this file uploaded?
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # 5. status: Current status of processing
     # We default to PENDING. Our Pandas script will update this later.


    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    # 6. message: Any notes or errors during processing
    message = models.TextField(blank=True, null=True, help_text="Processing notes or error messages will appear here.")

     # 7. output 
     # 
    processed_file = models.FileField(
        upload_to='results/%Y/%m/%d/', 
        null=True, 
        blank=True,
        help_text="The generated result file with ranks and analysis"
    )


    subject_chart = models.ImageField(upload_to='charts/', null=True, blank=True)
    passrate_chart = models.ImageField(upload_to='charts/', null=True, blank=True)

    reports_zip = models.FileField(
        upload_to = 'reports/%Y/%m/%d/',
        null =True,
        blank = True,
        help_text="A ZIP file containing individual student reports."
    
    )

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-uploaded_at'] # Newest uploads first
        verbose_name = "Exam File Upload"
        verbose_name_plural = "Exam File Uploads"