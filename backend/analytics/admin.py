from django.contrib import admin
from .models import ExamUpload

@admin.register(ExamUpload)
class ExamUploadAdmin(admin.ModelAdmin):
    # columns to show in the list view
    list_display = ('title', 'uploaded_at', 'status', 'message')
    # adds side filters for easy filtering
    list_filter = ('status', 'uploaded_at')
    # enables search box or bar to search by title or message
    search_fields = ('title', 'message')
     # Make the file read-only in admin so you don't accidentally change it
    readonly_fields = ('uploaded_at',)
    # default ordering of records
    ordering = ('-uploaded_at',)
