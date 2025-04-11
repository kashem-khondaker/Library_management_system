from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.generics import GenericAPIView
from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer, BookUpdateSerializer
from borrow_records.models import BorrowRecord
from borrow_records.serializers import BorrowRecordSerializer
from datetime import date, timedelta

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

class BookBorrowView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Book.objects.select_related('author', 'category').prefetch_related('borrow_records__member')
    serializer_class = BookSerializer

    def post(self, request, pk):
        """Handle borrowing a book."""
        try:
            book = self.get_object()
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if book.available_copies < 1:
            return Response(
                {'error': 'No copies available to borrow.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already has an active borrow record for this book
        existing_borrow = BorrowRecord.objects.filter(
            book=book,
            member=request.user.member,
            is_returned=False
        ).exists()
        
        if existing_borrow:
            return Response(
                {'error': 'You already have an active borrow record for this book.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        borrow_record = BorrowRecord.objects.create(
            book=book,
            member=request.user.member,
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=14)
        )
        book.available_copies -= 1
        book.save()
        
        return Response(
            BorrowRecordSerializer(borrow_record).data, 
            status=status.HTTP_200_OK
        )

class BookReturnView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def post(self, request, pk):
        """Handle returning a book."""
        try:
            book = self.get_object()
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        borrow_record = BorrowRecord.objects.filter(
            book=book, 
            member=request.user.member, 
            is_returned=False
        ).first()
        
        if not borrow_record:
            return Response(
                {'error': 'No active borrow record found for this book.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate fine if returned after due date
        fine = 0
        if date.today() > borrow_record.due_date:
            days_late = (date.today() - borrow_record.due_date).days
            fine = days_late * 10  # Assuming 10 currency units per day late

        borrow_record.is_returned = True
        borrow_record.return_date = date.today()
        borrow_record.fine = fine
        borrow_record.save()
        
        book.available_copies += 1
        book.save()
        
        return Response({
            'borrow_record': BorrowRecordSerializer(borrow_record).data,
            'fine': fine
        }, status=status.HTTP_200_OK)

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