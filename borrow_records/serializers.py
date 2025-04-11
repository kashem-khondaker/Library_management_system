from rest_framework import serializers
from .models import BorrowRecord
from members.serializers import MemberSerializer
from datetime import timedelta
from django.utils import timezone


class BorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRecord
        fields = ['id','book', 'member', 'borrow_date', 'due_date', 'return_date', 'is_returned', 'fine_amount']
        read_only_fields = ['borrow_date', 'due_date', 'return_date', 'is_returned', 'fine_amount']

    def validate(self, data):
        book = data.get('book')
        if not book:
            raise serializers.ValidationError("The book field is required.")
        if BorrowRecord.objects.filter(book=book, return_date__isnull=True).exists():
            raise serializers.ValidationError("This book is already borrowed and not yet returned.")
        return data

    def create(self, validated_data):
        validated_data['member'] = self.context['request'].user
        validated_data['due_date'] = timezone.now().date() + timedelta(days=15)
        return super().create(validated_data)
