from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from books.models import Book
from .models import BorrowRecord
from .serializers import BorrowRecordSerializer
from .customLogic import handle_borrow_request
from datetime import date, timedelta
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from borrow_records.models import BorrowRecord
from borrow_records.serializers import BorrowRecordSerializer

# class BookBorrowView(GenericAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Book.objects.select_related('author', 'category').prefetch_related('borrow_records__member')
#     serializer_class = BookSerializer

#     def post(self, request, pk):
#         """Handle borrowing a book."""
#         try:
#             book = self.get_object()
#         except Book.DoesNotExist:
#             return Response(
#                 {'error': 'Book not found.'}, 
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         if book.available_copies < 1:
#             return Response(
#                 {'error': 'No copies available to borrow.'}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Check if user already has an active borrow record for this book
#         existing_borrow = BorrowRecord.objects.filter(
#             book=book,
#             member=request.user.member,
#             is_returned=False
#         ).exists()
        
#         if existing_borrow:
#             return Response(
#                 {'error': 'You already have an active borrow record for this book.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         borrow_record = BorrowRecord.objects.create(
#             book=book,
#             member=request.user.member,
#             borrow_date=date.today(),
#             due_date=date.today() + timedelta(days=14)
#         )
#         book.available_copies -= 1
#         book.save()
        
#         return Response(
#             BorrowRecordSerializer(borrow_record).data, 
#             status=status.HTTP_200_OK
#         )

# class BookReturnView(GenericAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer

#     def post(self, request, pk):
#         """Handle returning a book."""
#         try:
#             book = self.get_object()
#         except Book.DoesNotExist:
#             return Response(
#                 {'error': 'Book not found.'}, 
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         borrow_record = BorrowRecord.objects.filter(
#             book=book, 
#             member=request.user.member, 
#             is_returned=False
#         ).first()
        
#         if not borrow_record:
#             return Response(
#                 {'error': 'No active borrow record found for this book.'}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Calculate fine if returned after due date
#         fine = 0
#         if date.today() > borrow_record.due_date:
#             days_late = (date.today() - borrow_record.due_date).days
#             fine = days_late * 10  # Assuming 10 currency units per day late

#         borrow_record.is_returned = True
#         borrow_record.return_date = date.today()
#         borrow_record.fine = fine
#         borrow_record.save()
        
#         book.available_copies += 1
#         book.save()
        
#         return Response({
#             'borrow_record': BorrowRecordSerializer(borrow_record).data,
#             'fine': fine
#         }, status=status.HTTP_200_OK)


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
