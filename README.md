# Bookmark Manager API

A RESTful API built with FastAPI that allows users to manage their bookmarks with JWT-based authentication.

## Features

- User registration and authentication with JWT
- CRUD operations for bookmarks
- Secure access to user-specific bookmarks
- SQLite database for development (easy migration to PostgreSQL)
- Docker support for containerization
- Swagger UI documentation

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Docker (optional, for containerization)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd bookmark-manager-api
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./bookmarks.db
```

## Rum migrations

1. Initialize the database with alembic

```
alembic init alembic
```

2. Update env.py file with database configuration and models

```
DATABASE_URL = os.getenv("DATABASE_URL")
```

3. Run and upgrade the migration tables

```
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Running the Application

1. Start the development server:

```bash
uvicorn main:app --reload
```

2. Access the API documentation at:

```
http://localhost:8000/docs
http://localhost:8000/redoc
```

## API Endpoints

### Authentication

- `POST /api/v1/users/register` - Register a new user
- `POST /api/v1/users/login` - Login and get JWT token (use swagger doc from)

### Users

- `GET /api/v1/users/me` - Get current user details
- `PUT /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/me` - Delete current user

### Bookmarks

- `POST /api/v1/bookmarks` - Create a new bookmark
- `GET /api/v1/bookmarks` - Get all bookmarks for current user
- `GET /api/v1/bookmarks/{bookmark_id}` - Get a specific bookmark
- `PUT /api/v1/bookmarks/{bookmark_id}` - Update a bookmark
- `DELETE /api/v1/bookmarks/{bookmark_id}` - Delete a bookmark

## Running with Docker

1. Build the Docker image:

```bash
docker build -t bookmark-manager-api .
```

2. Run the container:

```bash
docker run -p 8000:8000 bookmark-manager-api
```

## Testing

Run the test suite:

```bash
pytest
```

## Deployment

The application is configured for deployment to Google Cloud Run. The GitHub Actions workflow will automatically build and deploy the application when changes are pushed to the main branch.

## License

MIT
