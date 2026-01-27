
from django.urls import path
from .views import login_view, DocumentsView

urlpatterns = [
    path('login/', login_view.as_view(), name='login'),

    path('documents/', DocumentsView.as_view(), name='document-list')
]
