# DS Airlines - Modern Flight Booking System

This is a university project ("DS Airlines") refactored into a modern, production-ready full-stack application.

## Project Structure

The project is divided into two main components:

- **`backend/`**: A FastAPI application (Python) handling API requests, authentication, and database interactions with MongoDB.
- **`frontend/`**: A React application (TypeScript + Vite + Tailwind CSS) providing a modern user interface.

## Prerequisites

- **Docker** and **Docker Compose** (Recommended for easiest setup)
- **Node.js** (If running frontend locally without Docker)
- **Python 3.9+** (If running backend locally without Docker)

## How to Run (Using Docker) 🐳

This is the preferred way to run the application as it orchestrates the Backend, Frontend, and Database automatically.

1. **Navigate to the project root.**
2. **Build and start the services:**
   ```bash
   docker-compose up --build
   ```
3. **Access the application:**
   - **Frontend:** http://localhost:3000
   - **Backend API:** http://localhost:8000
   - **API Documentation (Swagger UI):** http://localhost:8000/docs

## How to Run Tests 

The backend tests are located in the `backend/tests/` directory.

### Option 1: Running inside Docker (Recommended)
You can run the tests inside the running backend container:
```bash
docker-compose exec backend pytest
```

### Option 2: Running locally
If you have Python installed and want to run tests locally:

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run pytest:
   ```bash
   pytest
   ```
   *Note: Ensure you have a MongoDB instance running or mocking configured if running integration tests.*

## API Documentation 

Once the backend is running, you can explore the interactive API documentation at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Technologies Used

- **Backend:** FastAPI, Uvicorn, Motor (Async MongoDB), Pydantic, JWT.
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Axios.
- **Database:** MongoDB.
- **DevOps:** Docker, Docker Compose, Nginx.
