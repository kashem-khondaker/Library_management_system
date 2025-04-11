from django.core.exceptions import ValidationError

def validate_single_borrow(user, book):
    """Ensure a user cannot borrow the same book multiple times."""
    if book in user.borrowed_books.all():
        raise ValidationError("You cannot borrow the same book multiple times.")

def validate_max_borrow_limit(user):
    """Ensure a user cannot borrow more than 7 books at a time."""
    if user.borrowed_books.count() >= 7:
        raise ValidationError("You cannot borrow more than 7 books at a time.")

def validate_return_all_books(user):
    """Ensure all borrowed books are returned before borrowing again."""
    if user.borrowed_books.filter(returned=False).exists():
        raise ValidationError("You must return all borrowed books before borrowing again.")
