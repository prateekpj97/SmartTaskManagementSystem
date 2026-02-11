# Smart Task Management System

A comprehensive task management web application built with Django, featuring asynchronous notifications, REST API, caching, and a modern Bootstrap interface.

## Features

- **User Authentication**: Secure login, signup, and profile management
- **Task Management**: Create, update, delete, and organize tasks with priorities and deadlines
- **Categories**: Organize tasks into customizable categories with color coding
- **Async Notifications**: Email reminders for upcoming deadlines using Celery
- **Daily Summaries**: Automated daily task summary emails
- **REST API**: Full-featured API for mobile app integration using Django REST Framework
- **Redis Caching**: Fast task list loading with Redis cache
- **Modern UI**: Responsive Bootstrap 5 dashboard with dynamic updates
- **Real-time Updates**: AJAX-powered task status changes

## Tech Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL
- **API**: Django REST Framework
- **Task Queue**: Celery + Redis
- **Cache**: Redis
- **Frontend**: Bootstrap 5, jQuery
- **Testing**: Pytest

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis Server

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd SmartTaskManagementSystem
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE smart_task_db;

# Exit PostgreSQL
\q
```

### 5. Configure Environment Variables

Update the `.env` file with your settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=smart_task_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Email (Update with your SMTP settings)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 6. Run Migrations

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 7. Create Superuser

```bash
python3 manage.py createsuperuser
```

### 8. Collect Static Files

```bash
python3 manage.py collectstatic --noinput
```

## Running the Application

### 1. Start Redis Server

```bash
redis-server
```

### 2. Start Celery Worker

```bash
celery -A smart_task_management worker --loglevel=info
```

### 3. Start Celery Beat (for scheduled tasks)

```bash
celery -A smart_task_management beat --loglevel=info
```

### 4. Start Django Development Server

```bash
python3 manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Running Tests

Run all tests with coverage:

```bash
pytest
```

Run specific test file:

```bash
pytest tasks/test_models.py
```

Run with coverage report:

```bash
pytest --cov=. --cov-report=html
```

## API Endpoints

### Authentication
- All API endpoints require authentication

### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create a new task
- `GET /api/tasks/{id}/` - Retrieve a task
- `PUT /api/tasks/{id}/` - Update a task
- `DELETE /api/tasks/{id}/` - Delete a task
- `POST /api/tasks/{id}/mark_completed/` - Mark task as completed
- `GET /api/tasks/statistics/` - Get task statistics
- `GET /api/tasks/overdue/` - Get overdue tasks
- `GET /api/tasks/upcoming/` - Get upcoming tasks

### Categories
- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create a new category
- `GET /api/categories/{id}/` - Retrieve a category
- `PUT /api/categories/{id}/` - Update a category
- `DELETE /api/categories/{id}/` - Delete a category

## Project Structure

```
SmartTaskManagementSystem/
├── smart_task_management/    # Project settings
├── tasks/                    # Tasks app
│   ├── models.py            # Task and Category models
│   ├── views.py             # Web views
│   ├── api_views.py         # API views
│   ├── serializers.py       # DRF serializers
│   ├── tasks.py             # Celery tasks
│   └── tests/               # Test files
├── accounts/                 # User authentication app
│   ├── models.py            # UserProfile model
│   ├── views.py             # Auth views
│   └── tests/               # Test files
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS)
└── requirements.txt         # Python dependencies
```

## License

MIT License

