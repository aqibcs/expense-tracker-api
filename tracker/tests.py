from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Expense

class ExpenseAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)
        self.expense = Expense.objects.create(user=self.user, amount=100, category='Food', description='Lunch', date='2024-01-01')

    def test_create_expense(self):
        response = self.client.post('/expenses/', {
            'amount': 50.0,
            'category': 'Transport',
            'description': 'Bus ticket',
            'date': '2024-10-25'
        })
        self.assertEqual(response.status_code, 201)
    
    def test_get_expense(self):
        response = self.client.get(f'/expenses/{self.expense.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['amount'], 100)
    
    def test_update_expense(self):
        response = self.client.put(f'/expenses/{self.expense.id}/', {
            'amount': 150,
            'category': 'Food',
            'description': 'Dinner',
            'date': '2024-10-25'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['amount'], 150)
    
    def test_delete_expense(self):
        response = self.client.delete(f'/expenses/{self.expense.id}/')
        self.assertEqual(response.status_code, 204)

    def test_summary_endpoint(self):
        response = self.client.get('/summary/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_expenses', response.data)
