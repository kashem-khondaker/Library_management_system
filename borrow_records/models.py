from django.db import models
from books.models import Book
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records')
    borrowed_at = models.DateTimeField(auto_now_add=True)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()
    is_returned = models.BooleanField(default=False)
    fine_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.member.username} borrowed {self.book.title}"

    @property
    def is_overdue(self):
        return not self.is_returned and self.due_date < date.today()

    @property
    def calculate_fine(self):
        if self.is_overdue:
            days_overdue = (date.today() - self.due_date).days
            return days_overdue * 10  
        return 0

    class Meta:
        ordering = ['-borrow_date']
