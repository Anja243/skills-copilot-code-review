# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Teacher-authenticated student registration and removal
- School-wide announcement banner sourced from MongoDB
- Teacher-authenticated announcement management (add/update/delete)

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/activities` | Get activities with optional day and time filters |
| GET | `/activities/days` | Get all scheduled days |
| POST | `/activities/{activity_name}/signup?email=student@mergington.edu&teacher_username=<username>` | Register a student to an activity (auth required) |
| POST | `/activities/{activity_name}/unregister?email=student@mergington.edu&teacher_username=<username>` | Remove a student from an activity (auth required) |
| POST | `/auth/login?username=<username>&password=<password>` | Sign in a teacher/admin user |
| GET | `/auth/check-session?username=<username>` | Validate a signed in user |
| GET | `/announcements` | Get active announcements visible to everyone |
| GET | `/announcements/all?teacher_username=<username>` | Get all announcements for management (auth required) |
| POST | `/announcements?teacher_username=<username>` | Create an announcement (auth required, JSON body) |
| PUT | `/announcements/{announcement_id}?teacher_username=<username>` | Update an announcement (auth required, JSON body) |
| DELETE | `/announcements/{announcement_id}?teacher_username=<username>` | Delete an announcement (auth required) |

## Data Model

The application uses MongoDB and initializes sample data in `backend/database.py` when collections are empty.

Data model overview:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

3. **Announcements** - Uses generated IDs:

   - Message text
   - Optional start date (`start_date`)
   - Required expiration date (`expires_on`)

Data persists in MongoDB across restarts.
