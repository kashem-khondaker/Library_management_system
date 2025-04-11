from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


from rest_framework import status
from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer, BookUpdateSerializer



class BookPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('author', 'category').prefetch_related('borrow_records__member')
    serializer_class = BookSerializer
    pagination_class = BookPagination
    filter_backends = [ filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'published_date', 'available_copies']
    search_fields = ['title', 'author__name', 'category__name']

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action."""
        if self.action in ['update', 'partial_update']:
            return BookUpdateSerializer
        return BookSerializer

    def create(self, request, *args, **kwargs):
        """Handle creating a new book."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Handle PUT (full update) requests with auto-filled existing data."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # Include existing instance data as defaults
        data = {**{field.name: getattr(instance, field.name) for field in instance._meta.fields}, **request.data}
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH (partial update) requests with auto-filled existing data."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    
    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]