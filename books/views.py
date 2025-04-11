from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer
from borrow_records.models import BorrowRecord
from borrow_records.serializers import BorrowRecordSerializer
from datetime import date

class BookPagination(PageNumberPagination):
    page_size = 10

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('author', 'category').prefetch_related('borrow_records__member')
    serializer_class = BookSerializer
    pagination_class = BookPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return []  # Allow anonymous users to view books

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def borrow(self, request, pk=None):
        book = self.get_object()
        if book.available_copies < 1:
            return Response({'error': 'No copies available to borrow.'}, status=400)

        borrow_record = BorrowRecord.objects.create(
            book=book,
            member=request.user.member,
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=14)  
        )
        book.available_copies -= 1
        book.save()
        return Response(BorrowRecordSerializer(borrow_record).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def return_book(self, request, pk=None):
        book = self.get_object()
        borrow_record = BorrowRecord.objects.filter(book=book, member=request.user.member, is_returned=False).first()
        if not borrow_record:
            return Response({'error': 'No active borrow record found for this book.'}, status=400)

        borrow_record.is_returned = True
        borrow_record.return_date = date.today()
        borrow_record.save()
        book.available_copies += 1
        book.save()
        return Response(BorrowRecordSerializer(borrow_record).data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
