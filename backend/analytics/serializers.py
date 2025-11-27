# backend/analytics/serializers.py
from rest_framework import serializers
from .models import ExamUpload

class ExamUploadSerializer(serializers.ModelSerializer):
    # 1. User Info: Show the username of the uploader (Read-only)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)

    # 2. File URL: Explicitly ensure the frontend gets a full URL
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamUpload
        # 3. Explicit Fields: Include ALL new fields we added to the model
        fields = [
            'id', 
            'title', 
            'slug',               # New: for pretty URLs
            'file', 
            'file_url',           # New: Explicit URL
            'uploaded_by_username', 
            'uploaded_at', 
            'updated_at',         # New: Track updates
            'status', 
            'message', 
            'analysis_summary',   # New: The JSON stats
            'processed_file', 
            'subject_chart', 
            'passrate_chart', 
            'reports_zip',
            'grading_scheme',    # New: Custom grading scheme
            'custom_ignore_columns'  # New: Safety valve for ignoring columns
        ]
        
        # 4. Protection: Ensure users cannot modify these fields via API
        read_only_fields = [
            'id', 
            'slug',
            'uploaded_by', 
            'uploaded_at', 
            'updated_at', 
            'status', 
            'message', 
            'analysis_summary', 
            'processed_file', 
            'subject_chart', 
            'passrate_chart', 
            'reports_zip'
        ]

    # 5. Custom Validation: Limit file size (e.g., 10MB)
    def validate_file(self, value):
        """
        Check that the uploaded file is not too large.
        """
        limit_mb = 10
        if value.size > limit_mb * 1024 * 1024:
            raise serializers.ValidationError(f"File too large. Size should not exceed {limit_mb} MB.")
        return value

    # Helper to get full URL for the file
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None