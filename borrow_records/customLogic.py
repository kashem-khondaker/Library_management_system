from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from books.models import Book
from .models import BorrowRecord
# from .policies.borrowing_policies import (
#     validate_single_borrow,
#     validate_max_borrow_limit,
#     validate_return_all_books,
# )

def apply_borrowing_policies(user, book):
    """
    Apply borrowing policies to ensure rules are followed.
    """
    # validate_single_borrow(user, book)
    # validate_max_borrow_limit(user)
    # validate_return_all_books(user)

def save_borrow_record(serializer):
    """
    Save the borrow record and handle exceptions.
    """
    try:
        serializer.save()
        return {
            "status": "success",
            "message": "Book borrowed successfully!",
            "data": serializer.data,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
        }

def handle_borrow_request(request, serializer_class, book_id=None, book_uuid=None):
    """
    Handle the logic for borrowing a book.
    """
    book = get_object_or_404(Book, id=book_id) if book_id else get_object_or_404(Book, uuid=book_uuid)
    apply_borrowing_policies(request.user, book)

    data = {
        "book": book.id,
        "member": request.user.id,
        **request.data,
    }
    serializer = serializer_class(data=data, context={'request': request})
    if serializer.is_valid():
        result = save_borrow_record(serializer)
        if result["status"] == "success":
            return {
                "response": result["data"],
                "status": status.HTTP_201_CREATED,
            }
        else:
            return {
                "response": {"error": result["message"]},
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
    return {
        "response": serializer.errors,
        "status": status.HTTP_400_BAD_REQUEST,
    }
