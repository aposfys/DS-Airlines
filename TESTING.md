# Testing Guide for DS Airlines

This document provides detailed instructions on how to test the DS Airlines application, ensuring both the backend API and frontend UI are functioning correctly.

## 1. Backend Testing 🧪

The backend is built with FastAPI and uses `pytest` for testing.

### Prerequisites
- Python 3.9+ installed.
- Dependencies installed: `pip install -r backend/requirements.txt`

### Running Unit Tests
Navigate to the `backend` directory and run pytest:

```bash
cd backend
pytest
```

This will run the tests located in `backend/tests/`, verifying:
- API server startup.
- Basic endpoint availability (e.g., health check).
- Validation logic (e.g., registration data format).

### Testing with In-Memory Database (Mock Mode)
To test the backend logic without a running MongoDB instance, you can enable the mock mode:

```bash
export USE_MOCK_DB=true
uvicorn main:app --reload
```
Then, you can manually test endpoints using Swagger UI at `http://localhost:8000/docs`.

## 2. Frontend Verification 🖥️

The frontend is a React application. Testing involves verifying user flows like Registration, Login, and Booking.

### Prerequisites
- Node.js 18+ installed.
- Dependencies installed: `cd frontend && npm install`

### Running the Frontend
Start the development server:

```bash
cd frontend
npm run dev
```
Access the app at `http://localhost:5173`.

### Manual Verification Steps

1. **Registration:**
   - Go to `/register`.
   - Fill in valid details (Password must have 8+ chars and a number).
   - Click "Register". You should be redirected to Login.

2. **Login:**
   - Go to `/login`.
   - Enter the credentials you just created.
   - Click "Sign In". You should be redirected to the Dashboard.

3. **Dashboard:**
   - Verify "Available Flights" are listed.
   - Click "Book" on a flight.
   - Verify the flight appears in "My Bookings".

4. **Cancellation:**
   - In "My Bookings", click "Cancel" on a booking.
   - Verify the booking disappears.

## 3. End-to-End Testing (Docker) 🐳

To test the entire stack integrated together as it would be in production:

1. **Start the Stack:**
   ```bash
   docker-compose up --build
   ```

2. **Run Backend Tests inside Container:**
   ```bash
   docker-compose exec backend pytest
   ```

3. **Access Application:**
   - Open `http://localhost:3000` in your browser.
   - The frontend will communicate with the backend container, which connects to the mongodb container.

## Troubleshooting

- **500 Internal Server Error on /docs:** usually relates to Pydantic validation schema issues. Ensure you have the latest code.
- **Connection Refused:** Ensure MongoDB is running or `MONGO_URL` is set correctly.
