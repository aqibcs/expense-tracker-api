from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # User Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Email reset URLs
    path('password-reset/', views.password_reset, name='password_reset'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),

    # Expense Management
    path('expenses/', views.create_expense, name='create_expense'),  # POST: create a new expense
    path('expenses/list/', views.list_expenses, name='list_expenses'),  # GET: list all expenses
    path('expenses/<int:id>/', views.get_expense, name='get_expense'),  # GET: retrieve a single expense
    path('expenses/<int:id>/update/', views.update_expense, name='update_expense'),  # PUT: update an expense
    path('expenses/<int:id>/delete/', views.delete_expense, name='delete_expense'),  # DELETE: delete an expense
    path('expenses/summary/', views.expense_summary, name='expense_summary'),  # GET: summary of expenses
]
