# fastapi_tutorial

Core Features
Asynchronous API: High-performance endpoints built with FastAPI.

Book Management: Full CRUD (Create, Read, Update, Delete) operations for a book catalog.

Structured Architecture: Separation of concerns using Routes, Services, and Schemas.

Dependency Injection: Uses FastAPI’s Depends for managing database sessions and authentication.

Background Tasks: Integrated Celery with Redis for handling long-running tasks like sending emails.

Key Technical Concepts Included
Schema Validation: Using Pydantic (BookCreateModel, BookResponseModel) to ensure data integrity.

Service Layer Pattern: Keeping routes thin by moving database logic into dedicated service classes.
Gemini said
To update your README for the fastapi_tutorial repository, here is a summary based on the architecture and flow of the tutorial we have been discussing. This tutorial focuses on building a Production-Ready Book Management API with a clean, decoupled architecture.

Project Summary for README
Core Features
Asynchronous API: High-performance endpoints built with FastAPI.

Book Management: Full CRUD (Create, Read, Update, Delete) operations for a book catalog.

Structured Architecture: Separation of concerns using Routes, Services, and Schemas.

Dependency Injection: Uses FastAPI’s Depends for managing database sessions and authentication.

Background Tasks: Integrated Celery with Redis for handling long-running tasks like sending emails.

Project Structure
Plaintext
src/
├── auth/ # Authentication logic & Role-based Access Control (RBAC)
├── books/ # Book domain logic
│ ├── routes.py # API endpoints
│ ├── schemas.py # Pydantic models for request/response validation
│ └── service.py # Business logic and database interactions
├── db/ # Database configuration and SQLAlchemy models
├── tasks/ # Celery task definitions (e.g., email service)
├── config.py # Environment variables and app configuration
└── main.py # App entry point and Celery app initialization
Key Technical Concepts Included

Schema Validation: Using Pydantic (BookCreateModel, BookResponseModel) to ensure data integrity.

Service Layer Pattern: Keeping routes thin by moving database logic into dedicated service classes.

Asynchronous Background Work: Offloading email notifications to Celery workers to keep API responses fast.

ow to Run (Brief)
Add all necessary .env variables
Set up a virtual environment using uv
Install dependencies: uv sync
run migrations: alembic upgrade head
Start API: fastapi dev src
Start Celery: celery -A src.main.c_app worker
