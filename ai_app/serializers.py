
from rest_framework import serializers

class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for PDF upload."""
    file = serializers.FileField(
        help_text="PDF file to upload (max 10MB)"
    )
    
    def validate_file(self, value):
        """Validate file type and size."""
        # Check file extension
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 10MB.")
        
        return value
