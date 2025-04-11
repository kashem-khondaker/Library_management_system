from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from books.models import Book
from .models import BorrowRecord
from .serializers import BorrowRecordSerializer
from .customLogic import handle_borrow_request
from datetime import date

class BorrowRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing BorrowRecord objects.
    """
    queryset = BorrowRecord.objects.select_related('member', 'book')
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        """
        Allow admins to view all records, but restrict regular users to their own records.
        """
        if self.request.user.is_staff:
            return BorrowRecord.objects.select_related('member', 'book')
        return BorrowRecord.objects.filter(member=self.request.user).select_related('book')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_borrowed_books(self, request):
        """
        Show the list of books borrowed by the authenticated user.
        """
        borrowed_books = BorrowRecord.objects.filter(member=request.user).select_related('book')
        serializer = self.get_serializer(borrowed_books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def borrow_book(self, request):
        """
        Handle borrowing a book by ID.
        """
        result = handle_borrow_request(request, self.get_serializer_class(), book_id=request.data.get('book'))
        return Response(result["response"], status=result["status"])

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def borrow_specific_book(self, request, pk=None):
        """
        Handle borrowing a specific book by UUID.
        """
        result = handle_borrow_request(request, self.get_serializer_class(), book_uuid=pk)
        return Response(result["response"], status=result["status"])

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def return_book(self, request, pk=None):
        """
        Handle returning a borrowed book by BorrowRecord ID.
        """
        borrow_record = get_object_or_404(BorrowRecord, pk=pk, member=request.user)
        if borrow_record.is_returned:
            return Response({"detail": "This book has already been returned."}, status=status.HTTP_400_BAD_REQUEST)
        
        borrow_record.is_returned = True
        borrow_record.return_date = date.today()
        borrow_record.save()

        # Delete the borrow record after marking it as returned
        borrow_record.delete()

        return Response({"detail": "Book returned successfully and borrow record deleted."}, status=status.HTTP_200_OK)
