from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.utils.dateparse import parse_date
from django.db.models import Sum
from rest_framework_simplejwt.tokens import RefreshToken
from .forms import UserLoginForm, UserRegistrationForm
from .models import Expense
from .serializers import ExpenseSerializer


# Function to generate JWT tokens for authenticated users
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user by validating the user registration form,
    creating a new user, and generating JWT tokens for the new user.
    """
    user_form = UserRegistrationForm(data=request.data)
    if user_form.is_valid():
        new_user = user_form.save(commit=False)
        new_user.set_password(user_form.cleaned_data['password1'])
        new_user.save()
        tokens = get_tokens_for_user(new_user)

        return Response(
            {
                "message": "User registered successfully.",
                "token": tokens
            },
            status=status.HTTP_201_CREATED)
    else:
        return Response(user_form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticate a user and generate JWT tokens upon successful login.
    """
    login_form = UserLoginForm(data=request.data)
    if login_form.is_valid():
        username = login_form.cleaned_data['username']
        password = login_form.cleaned_data['password']

        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_active:
                tokens = get_tokens_for_user(user)
                return Response(
                    {
                        "message": "Login successful",
                        "tokens": tokens
                    },
                    status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Account is inactive'},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'Invalid username or password'},
                            status=status.HTTP_401_UNAUTHORIZED)
    return Response(login_form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Retrieve the authenticated user's profile information.
    """
    user = request.user
    return Response({"username": user.username}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_expense(request):
    """
    Create a new expense for the authenticated user.
    """
    serializer = ExpenseSerializer(data=request.data,
                                   context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(
            {
                "message": "Expense created successfully",
                "expense": serializer.data
            },
            status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_expenses(request):
    """
    List all expenses for the authenticated user with optional date filtering.
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    try:
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)
    except ValueError:
        return Response({"error": "Invalid date format"},
                        status=status.HTTP_400_BAD_REQUEST)

    expenses = Expense.objects.filter(user=request.user)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    serialized_expenses = ExpenseSerializer(expenses, many=True).data
    return Response({"expenses": serialized_expenses},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expense(request, id):
    """
    Retrieve a specific expense by ID for the authenticated user.
    """
    try:
        expense = Expense.objects.get(id=id, user=request.user)
        return Response(ExpenseSerializer(expense).data,
                        status=status.HTTP_200_OK)
    except Expense.DoesNotExist:
        return Response({"error": "Expense not found"},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_expense(request, id):
    """
    Update an expense by ID for the authenticated user.
    """
    try:
        expense = Expense.objects.get(id=id, user=request.user)
    except Expense.DoesNotExist:
        return Response({"error": "Expense not found"},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = ExpenseSerializer(expense,
                                   data=request.data,
                                   partial=True,
                                   context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Expense updated successfully",
                "expense": serializer.data
            },
            status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_expense(request, id):
    """
    Delete an expense by ID for the authenticated user.
    """
    try:
        expense = Expense.objects.get(id=id, user=request.user)
        expense.delete()
        return Response({"message": "Expense deleted successfully"},
                        status=status.HTTP_204_NO_CONTENT)
    except Expense.DoesNotExist:
        return Response({"error": "Expense not found"},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_summary(request):
    """
    Retrieve a summary of expenses for the authenticated user, including totals and insights.
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    try:
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)
    except ValueError:
        return Response({"error": "Invalid date format"},
                        status=status.HTTP_400_BAD_REQUEST)

    expenses = Expense.objects.filter(user=request.user)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    categorized_totals = expenses.values('category').annotate(
        total=Sum('amount')).order_by('-total')

    highest_spending_category = (max(
        categorized_totals, key=lambda x: x['total'], default=None) or {
            "category": None,
            "total": 0
        })

    response_data = {
        "total_expenses": total_expenses,
        "categorized_totals": list(categorized_totals),
        "insights": {
            "highest_spending_category": highest_spending_category['category'],
            "highest_spending_amount": highest_spending_category['total'],
        }
    }

    return Response(response_data, status=status.HTTP_200_OK)
