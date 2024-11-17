# Personal Finance Tracker
A Django-based personal finance tracker application that allows users to track their expenses, view the categorized summaries, and gain financial insights. This project features `JWT-based` authentication and `PostgreSQL` integration.

## Features:
- **User Registration & Authentication:** Register new users and authenticate existing ones using `JSON Web Tokens (JWT)`.
- **Expense Management:** Create, retrieve, update, and delete expense entries with optional filtering.
- **Expense Summary:** View a summary of expenses including the total amount spent, breakdown by category, and insights like the highest spending category.
- **PostgreSQL:** Uses `PostgreSQL` for secure scalable data storage.


## Setup Instructions
### Prerequisites
1. **Python 3.8+** is required.
2. **PostgreSQL** should be installed and running locally or accessible via network.

### Step 1: Clone the Repository
```bash
git clone 
cd personal-finance-tracker
```

### Step 2: Create and Activate a Virtual Environment
```bash
python -m venv env
source env/bin/activate
# On windows, use
env\scripts\activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure PostgreSQL
1. Create a PostgreSQL database:
```sql
CREATE DATABASE finance_tracker;
```
2. In `finance_tracker/setting.py`, update the `DATABASE` configuration:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finance',
        'USER': 'postgres_username',
        'PASSWORD': 'postgres_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Step 5: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Run the Development Server
```bash
python manage.py runserver
```
The server should be running at `http://127.0.0.1:8000/`.


# Api Endpoints
All API endpoints use `JWT-based` authentication, which should be included in the headers as:
```http
Authorization: Bearer <your_jwt_token>
```

## Authentication Endpoints
1. **Register a New User**
- **Endpoint:** `POST /register/`
- **Description:** Register a new user account
- **Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```
- **Response:**
```json
{
    "message": "User registered successfully",
    "token": "jwt_token"
}
```

2. **Login**
- **Endpoint:** `POST /login/`
- **Description:** Authentication an existing user and receive a `JWT` token.
- **Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```
- **Response:**
```json
{
    "token": "jwt_token"
}
```

3. **User Profile**
- **Endpoint:** `GET /profile/`
- **Description:** Retrieve the authenticated user's profile.
- **Headers:**
```http
AuthorizationL Bearer <jwt_token>
```
- **Response:**
```json
{
    "username": "string",
    "email": "string"
}
```


# Expense Management Endpoints
1. **Create an Expense**
- **Endpoint:** `POST /expenses/`
- **Description:** Add a new expense entry.
- **Headers:**
```http
Authorization: Bearer <jwt_token>
```

- **Request Body:**
```json
{
    "amount": 100.0,
    "category": "Food",
    "description": "Lunch with friends",
    "date": "YYYY-MM-DD"
}
```

2. **List All Expenses**
- **Endpoint:** `GET /expenses/`
- **Description:** Retrieve a list of all expenses with optional date filtering.
- **Headers:**
```http
Authorization: Bearer <jwt_token>
```
- **Query Parameters** (optional):
    - `start_date` (YYYY-DD-MM): Start date for filtering.
    - `end_date` (YYYY-DD-MM): End date for filtering.
- **Response:**
```json
[
    {
        "id": 1,
        "amount": 100.0,
        "category": "Food",
        "description": "Lunch with friends",
        "date": "YYYY-MM-DD"
    },
    ...
]
```

3. **Retrieve a Specific Expense**
- **Endpoint:** `GET /expenses/{id}/`
- **Description:** Retrieve details of a specific expense by its ID.
- **Headers:**
```http
Authorization: Bearer <jwt_token>
```
- **Response:**
```json
{
    "id": 1,
    "amount": 100.0,
    "category": "Food",
    "description": "Lunch with friends",
    "date": "YYYY-MM-DD"
}
```

4. **Update an Expense**
- **Endpoint:** `PUT /expenses/{id}/`
- **Description:** Update an existing expense entry.
- **Headers:**
```http
Authorization: Bearer <jwt_token>
```
- **Request Body:**
```json
{
    "amount": 150.0,
    "category": "Entertainment",
    "description": "Movie ticket",
    "date": "YYYY-MM-DD"
}
```

5. **Delete an Expense**
- **Endpoint:** `DELETE /expense/{id}/`
- **Description:** Delete an expense entry by its ID.
- **Headers:**
```http
Authorization: Bearer <jwt_token>
```


# Expense Summary Endpoint
## Get Expense Summary
- **Endpoint:** `GET /summary/`
- **Description:** Get a summary of expenses for the authenticated user, including total amount spent, categorized breakdown, and insights.
- **Headers:**
```http
Authorization: Bearer <jwt_token>
```
- **Query Parameters** (optional):
    - `start_date` (YYYY-MM-DD): Start date for summary calculation.
    - `end_date` (YYYY-MM-DD): End date for summary calculation.
- **Response:**
```json
{
    "total_expenses": 1500.75,
    "categorized_totals": [
        {"category": "Food", "total": 500.25},
        {"category": "Entertainment", "total": 300.50},
        {"category": "Rent", "total": 700.00}
    ],
    "insights": {
        "highest_spending_category": "Rent",
        "highest_spending_amount": 700.00
    }
}
```

# Testing
To ensure the correctness of API functionality, run test as follows:
1. **Run Tests:**
```bash
python manage.py test
```
2. **Test Coverage:**
- Authentication endpoints: registration and login.
- Expense management endpoints: create, retrieve, update, delete, and list expenses.
- Summary endpoint: calculate expense summaries with and without date filters.