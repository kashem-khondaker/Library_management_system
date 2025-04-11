from rest_framework import serializers
from .models import Book, Category
from borrow_records.models import BorrowRecord
from authors.models import Author

class SimpleBorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRecord
        fields = ['id', 'book', 'member']

class SimpleAuthorRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name']


class BookSerializer(serializers.ModelSerializer):
    author = SimpleAuthorRecordSerializer(read_only=True)  
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=SimpleAuthorRecordSerializer.Meta.model.objects.all(), write_only=True, source='author'
    )  
    borrow_records = SimpleBorrowRecordSerializer(many=True, read_only=True)
    ISBN = serializers.CharField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author_id', 'ISBN', 'category', 'published_date', 'total_copies', 'available_copies', 'cover_image', 'availability_status', 'author', 'borrow_records']
        read_only_fields = ['availability_status', 'ISBN', 'borrow_records']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']