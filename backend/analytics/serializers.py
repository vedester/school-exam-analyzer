from rest_framework import serializers
from .models import ExamUpload

class ExamUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamUpload
        fields = ['id', 'title', 'file', 'uploaded_at',
                   'status', 'message', 'processed_file',
                   'subject_chart','passrate_chart']
        read_only_fields = ['uploaded_at', 'status', 'message',
                             'processed_file','subject_chart',
                             'passrate_chart']
        