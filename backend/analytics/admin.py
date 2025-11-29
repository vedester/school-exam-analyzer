from django.contrib import admin
from .models import ExamUpload

@admin.register(ExamUpload)
class ExamUploadAdmin(admin.ModelAdmin):
    # columns to show in the list view
    list_display = ('title', 'uploaded_by', 'uploaded_at','status', 'message')
    # adds side filters for easy filtering
    list_filter = ('status', 'uploaded_at' ,'uploaded_by')
    # enables search box or bar to search by title or message
    # You can now type a username or email in the search box to find their files
    search_fields = ('title', 'message', 'uploaded_by__username', 'uploaded_by__email')
    
     # Make the file read-only in admin so you don't accidentally change it
    readonly_fields = ('uploaded_at','uploaded_by')
    # default ordering of records
    ordering = ('-uploaded_at',)
