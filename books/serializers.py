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
        read_only_fields = ['availability_status', 'ISBN', 'borrow_records' , 'available_copies' , 'published_date']


    def create(self, validated_data):
        """Set available_copies to total_copies during creation."""
        validated_data['available_copies'] = validated_data.get('total_copies', 0)
        return super().create(validated_data)

class BookUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating book details.
    Ensures total copies are non-negative and updates available copies accordingly.
    """
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'total_copies', 'cover_image', 'availability_status']
        read_only_fields = ['availability_status']
    
    def validate(self, data):
        if 'total_copies' in data and data['total_copies'] <= 0:
            raise serializers.ValidationError("Total copies cannot be negative or zero.")
        return data

    def update(self, instance, validated_data):
        total_copies = validated_data.get('total_copies')
        if total_copies is not None:
            validated_data['available_copies'] = total_copies
        return super().update(instance, validated_data)

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for book categories.
    Provides basic details such as ID and name.
    """
    class Meta:
        model = Category
        fields = ['id', 'name']