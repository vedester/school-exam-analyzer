from rest_framework import serializers
from .models import ExamUpload

class ExamUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamUpload
        fields = ['id', 'title', 'file', 'uploaded_at', 'status', 'message', 'processed_file']
        read_only_fields = ['uploaded_at', 'status', 'message', 'processed_file']
        