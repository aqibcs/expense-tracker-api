from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail
from finance_tracker import settings
from .forms import UserLoginForm, UserRegistrationForm, PasswordResetForm, SetNewPasswordForm
from .models import Expense
from .serializers import ExpenseSerializer
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib.auth import logout



def home(request):
    """
    Redirect to dashboard if user is authenticated, otherwise to login page
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(data=request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password1'])
            new_user.save()
            # Auto login the user
            auth_login(request, new_user)
            messages.success(request, "Registration successful! Welcome to Finance Tracker.")
            return redirect('dashboard')
        else:
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        user_form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': user_form})


def login(request):
    if request.method == 'POST':
        login_form = UserLoginForm(data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user:
                if user.is_active:
                    auth_login(request, user)
                    messages.success(request, "Login successful!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Account is inactive.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        login_form = UserLoginForm()
    
    return render(request, 'auth/login.html', {'form': login_form})


@login_required
def profile(request):
    if request.method == 'POST':
        # Process profile update form
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    
    user = request.user
    total_expenses = Expense.objects.filter(user=user).count()
    total_spent = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get most common category
    categories = Expense.objects.filter(user=user).values('category').annotate(
        count=Sum('amount')).order_by('-count')
    most_common_category = categories[0]['category'] if categories.exists() else None
    
    context = {
        'user': user,
        'total_expenses': total_expenses,
        'total_spent': total_spent,
        'most_common_category': most_common_category
    }
    
    return render(request, 'profile.html', context)


def password_reset(request):
    if request.method == 'POST':
        email_form = PasswordResetForm(data=request.POST)
        if email_form.is_valid():
            email = email_form.cleaned_data['email']
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={"uidb64": uid, "token": token})
            )

            subject = 'Password Reset Request'
            message = (
                f'Hello {user.username}, \n\n'
                'You requested a password reset. Click the link below to reset your password:\n'
                f'{reset_link}\n\n'
                'Thank You!\n\n'
                'If you did not request this change, please ignore this message.')
            send_mail(subject,
                    message,
                    settings.EMAIL_HOST_USER, [email],
                    fail_silently=False)
            messages.success(request, "Password reset email sent. Please check your inbox.")
            return redirect('login')
        else:
            for field, errors in email_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        email_form = PasswordResetForm()
    
    return render(request, 'auth/password_reset.html', {'form': email_form})


def password_reset_confirm(request, uidb64, token):
    if request.method == 'POST':
        form = SetNewPasswordForm(data=request.POST, uidb64=uidb64, token=token)
        if form.is_valid():
            form.save()
            messages.success(request, "Password has been reset successfully. You can now login.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SetNewPasswordForm(uidb64=uidb64, token=token)
    
    return render(request, 'auth/password_reset_confirm.html', {'form': form})


def user_logout(request):
    """
    Log the user out and redirect to login page
    """
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)
    except ValueError:
        messages.error(request, "Invalid date format")
        start_date = None
        end_date = None
    
    # Filter expenses
    expenses = Expense.objects.filter(user=user)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    
    # Calculate summary
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    categorized_totals = expenses.values('category').annotate(
        total=Sum('amount')).order_by('-total')
    
    highest_spending_category = (max(
        categorized_totals, key=lambda x: x['total'], default=None) if categorized_totals else {
            "category": None,
            "total": 0
        })
    
    summary = {
        "total_expenses": total_expenses,
        "categorized_totals": list(categorized_totals),
        "insights": {
            "highest_spending_category": highest_spending_category.get('category'),
            "highest_spending_amount": highest_spending_category.get('total', 0),
        }
    }
    
    # Get monthly data for trends
    one_year_ago = datetime.now().date() - timedelta(days=365)
    monthly_data = Expense.objects.filter(
        user=user, 
        date__gte=one_year_ago
    ).values('date__year', 'date__month').annotate(
        total=Sum('amount')
    ).order_by('date__year', 'date__month')
    
    formatted_monthly_data = []
    for data in monthly_data:
        month_date = datetime(data['date__year'], data['date__month'], 1)
        formatted_monthly_data.append({
            'month': month_date.strftime('%b %Y'),
            'total': data['total']
        })
    
    # Recent expenses
    recent_expenses = expenses.order_by('-date')[:5]
    
    # Calculate expense count and average
    expense_count = expenses.count()
    average_expense = total_expenses / expense_count if expense_count > 0 else 0
    
    context = {
        'summary': summary,
        'monthly_data': formatted_monthly_data,
        'recent_expenses': recent_expenses,
        'expense_count': expense_count,
        'average_expense': average_expense
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def create_expense(request):
    if request.method == 'POST':
        data = request.POST.copy()
        # Add user to data
        serializer = ExpenseSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            messages.success(request, "Expense created successfully!")
            return redirect('list_expenses')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render(request, 'expenses/expense_form.html', {'today': today})


@login_required
def list_expenses(request):
    user = request.user
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')
    
    try:
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)
    except ValueError:
        messages.error(request, "Invalid date format")
        start_date = None
        end_date = None
    
    expenses = Expense.objects.filter(user=user)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if category:
        expenses = expenses.filter(category=category)
    
    expenses = expenses.order_by('-date')
    
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})


@login_required
def get_expense(request, id):
    try:
        expense = get_object_or_404(Expense, id=id, user=request.user)
        return render(request, 'expenses/expense_detail.html', {'expense': expense})
    except:
        messages.error(request, "Expense not found")
        return redirect('list_expenses')


@login_required
def update_expense(request, id):
    """
    Update an existing expense
    """
    try:
        # Find the expense
        expense = Expense.objects.filter(id=id).first()
        
        if not expense:
            messages.error(request, f"Expense with ID {id} not found in the database")
            return redirect('list_expenses')
            
        # Check if it belongs to the current user
        if expense.user.id != request.user.id:
            messages.error(request, "You don't have permission to edit this expense")
            return redirect('list_expenses')
        
        if request.method == 'POST':
            data = request.POST.copy()
            serializer = ExpenseSerializer(expense, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                messages.success(request, "Expense updated successfully!")
                return redirect('list_expenses')
            else:
                for field, errors in serializer.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        
        today = datetime.now().strftime('%Y-%m-%d')
        return render(request, 'expenses/expense_form.html', {'expense': expense, 'today': today})
    
    except Exception as e:
        print(f"Error updating expense: {str(e)}")
        messages.error(request, f"Error updating expense: {str(e)}")
        return redirect('list_expenses')



@login_required
def delete_expense(request, id):
    try:
        expense = get_object_or_404(Expense, id=id, user=request.user)
        
        if request.method == 'POST':
            expense.delete()
            messages.success(request, "Expense deleted successfully!")
            return redirect('list_expenses')
        
        # For GET requests, show confirmation page
        return render(request, 'expenses/expense_detail.html', {'expense': expense})
    except:
        messages.error(request, "Expense not found")
        return redirect('list_expenses')
