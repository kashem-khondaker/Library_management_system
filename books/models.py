from django.db import models
from authors.models import Author
import uuid

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Use UUID for unique and unpredictable IDs
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    ISBN = models.CharField(max_length=13, unique=True, default=uuid.uuid4().hex[:13])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    published_date = models.DateField(auto_now_add=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    availability_status = models.BooleanField(default=True, editable=False)  # Make field non-editable

    def save(self, *args, **kwargs):
        if not self.ISBN:
            self.ISBN = uuid.uuid4().hex[:13]  # Generate a unique 13-character ISBN
        self.availability_status = self.available_copies > 0  # Auto-update availability_status
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

