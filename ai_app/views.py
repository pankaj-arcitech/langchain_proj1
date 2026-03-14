import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import DocumentUploadSerializer
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.permissions import IsAuthenticated


class DocumentsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            # Save file temporarily
            file_name = f"{uuid.uuid4()}_{uploaded_file.name}"
            file_path = default_storage.save(
                f"pdfs/{request.user.id}/{file_name}",
                ContentFile(uploaded_file.read())
            )
            
            full_path = default_storage.path(file_path)

        return Response({"message": "File uploaded successfully", 'path': full_path}, status=200)