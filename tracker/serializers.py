from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = [
            'id', 'user', 'amount', 'category', 'description', 'date',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_amount(self, value):
        """
        Ensure the amount is non-negative.
        """
        if value < 0:
            raise serializers.ValidationError("Amount must be non-negative.")
        return value
