# Anievent API

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-red.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-green.svg)
![Pydantic Schema](https://img.shields.io/badge/Pydantic-2.12.5-purple.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-orange.svg)

Anevent is a REST API for an event management app.
It is an app where users can book an event manager to manage their event,
choose location and decorators, leave a public review, and make payments.

## Project Structure
```
Anevent API
├── alembic/
├── app/
│   ├── routes/
│   │   └──user.py
│   │
│   ├── services/
│   │   └── users.py
│   │
│   ├── schemas/
│   │   └── users.py
│   │
│   ├── models/
│   │   └── users.py
│   │
│   ├── auth/
│   │   ├── auth.py
│   │   └── dependency.py
│   │
│   ├── middleware/
│   │   └── request_tracking.py
│   │
│   ├── utils/
│   │   └── otp.py
│   │
│   ├── database.py
│   │
│   └── main.py
│
└── README.md
```

##  Features

### Core Functionality
- **User Management**: Registration, authentication, profile management

### Key Highlights
- **JWT Authentication**: Secure token-based authentication
- **Database Migrations**: Alembic integration for schema versioning
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Data Validation**: Robust input validation with Pydantic schemas

##  Architecture

### Tech Stack
- **Framework**: FastAPI (Python 3.13)
- **Database**: PostgreSQL 
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT tokens with bcrypt password hashing
- **Migration**: Alembic
- **Documentation**: OpenAPI/Swagger UI


##  Prerequisites (Requirements to successfully run the app in local machine)

- vs.code or pycharm editor
- Python 3.13+
- PostgreSQL (database)
- pip or pipenv for dependency management

##  How to Start

### 1. Clone the Repository
```bash
git clone https://github.com/esther-anierobi/anevent.git
cd anevent
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv menv

# Activate virtual environment
# On Windows:
menv\Scripts\activate
# On macOS/Linux:
source menv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create an .env file with values on .env.example file

### 5. Set Up Database
```bash
# Run migrations
alembic upgrade head
```

### 6. Run the Application
```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 7. Access the API
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive SwaggerUI Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`