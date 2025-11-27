# backend/analytics/views.py
import threading
from rest_framework import viewsets, permissions, status, parsers, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User



from .models import ExamUpload
from .serializers import ExamUploadSerializer, RegisterSerializer
# Import the analysis engine
from .analysis import process_exam_file 


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # IMPORTANT: Allow anonymous users
    serializer_class = RegisterSerializer
    


class ExamUploadViewSet(viewsets.ModelViewSet):
    serializer_class = ExamUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ExamUpload.objects.all()
        return ExamUpload.objects.filter(uploaded_by=user)

    def perform_create(self, serializer):
        """
        Save the file, then immediately trigger analysis in a background thread.
        """
        # 1. Save to DB
        instance = serializer.save(uploaded_by=self.request.user)
        
        # 2. Trigger Analysis (Background Thread)
        # In a massive scale app (1000s of uploads/min), use Celery.
        # For a startup/SaaS, Threading is perfect and free.
        self._trigger_analysis(instance)

    @action(detail=True, methods=['post'])
    def retry_processing(self, request, id=None):
        """
        Manually retry analysis if it failed.
        """
        exam = self.get_object()
        
        if exam.status == ExamUpload.Status.PROCESSING:
             return Response(
                {"detail": "File is already being processed."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reset and run
        exam.status = ExamUpload.Status.PENDING
        exam.message = "Retry started..."
        exam.save()
        
        self._trigger_analysis(exam)
        
        serializer = self.get_serializer(exam)
        return Response(serializer.data)

    def _trigger_analysis(self, instance):
        """
        Helper to run the heavy analysis in a separate thread
        so the user gets a generic '201 Created' response instantly.
        """
        instance.status = ExamUpload.Status.PROCESSING
        instance.save()
        
        task = threading.Thread(target=process_exam_file, args=(instance,))
        task.start()