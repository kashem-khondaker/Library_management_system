from django.shortcuts import render
from rest_framework import viewsets
from .models import Author
from .serializers import AuthorSerializer

# Create your views here.

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        # Optionally filter authors by name query parameter
        queryset = super().get_queryset()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset
