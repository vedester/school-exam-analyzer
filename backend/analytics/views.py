# backend/analytics/views.py
from rest_framework import viewsets,parsers
from .serializers import ExamUploadSerializer
from .models import ExamUpload
from .analysis import process_exam_file 

# Create your views here.

class ExamUploadViewset(viewsets.ModelViewSet):
    queryset = ExamUpload.objects.all()
    serializer_class = ExamUploadSerializer
    # Allow file uploads via multipart/form-data
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        #When a file is uploaded we save it
        instance=serializer.save()
        
        instance.status = 'PROCESSING'
        instance.save()
        
        process_exam_file(instance)
        


