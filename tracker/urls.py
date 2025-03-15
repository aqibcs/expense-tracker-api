from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Root URL (Homepage) - Redirect to dashboard if logged in, otherwise to login
    path('', views.home, name='home'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # User Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),

    # Password Reset URLs
    path('password-reset/', views.password_reset, name='password_reset'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),

    # Expense Management
    path('expenses/create/', views.create_expense, name='create_expense'),  
    path('expenses/', views.list_expenses, name='list_expenses'),  
    path('expenses/<int:id>/', views.get_expense, name='get_expense'),  
    path('expenses/<int:id>/update/', views.update_expense, name='update_expense'), 
    path('expenses/<int:id>/delete/', views.delete_expense, name='delete_expense'),  
    path('expenses/summary/', views.dashboard, name='expense_summary'),  
]
