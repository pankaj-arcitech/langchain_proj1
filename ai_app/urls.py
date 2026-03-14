
from django.urls import path
from .views import DocumentsView

urlpatterns = [
    path('documents/', DocumentsView.as_view(), name='document-list'),
]
