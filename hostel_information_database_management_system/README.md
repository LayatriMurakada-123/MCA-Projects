# Hostel Information Database Management System

A complete beginner-friendly full-stack Hostel Information Database Management System using:

- Frontend: HTML5, CSS3, JavaScript
- Backend: Python Flask REST API
- Database: SQLite (SQL)
- API: RESTful JSON endpoints

## Features

1. Dashboard
2. Student management
3. Room management and vacancy tracking
4. Staff management
5. Hostel fee management
6. Complaint management
7. REST APIs for CRUD operations
8. Responsive UI
9. SQL database schema and sample data

## Project structure

```
hostel_information_database_management_system/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── templates/
│   └── static/
├── database/
│   └── schema.sql
├── frontend/
└── README.md
```

## How to run

### 1. Install Python

Python 3.10+ is recommended.

### 2. Open terminal in the project folder

Windows:
```
cd hostel_information_database_management_system
```

### 3. Create a virtual environment (recommended)

```
python -m venv venv
```

Activate:

Windows CMD:
```
venv\Scripts\activate
```

PowerShell:
```
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```
pip install -r backend/requirements.txt
```

### 5. Start the application

```
python backend/app.py
```

The application will initialize `database/hostel.db` automatically.

### 6. Open in browser

```
http://127.0.0.1:5000
```

## API endpoints

### Dashboard
- GET `/api/dashboard`

### Students
- GET `/api/students`
- POST `/api/students`
- PUT `/api/students/<id>`
- DELETE `/api/students/<id>`

### Rooms
- GET `/api/rooms`
- POST `/api/rooms`
- PUT `/api/rooms/<id>`
- DELETE `/api/rooms/<id>`

### Staff
- GET `/api/staff`
- POST `/api/staff`
- DELETE `/api/staff/<id>`

### Fees
- GET `/api/fees`
- POST `/api/fees`
- PUT `/api/fees/<id>`

### Complaints
- GET `/api/complaints`
- POST `/api/complaints`
- PUT `/api/complaints/<id>`

## Notes

SQLite is used so the project can run immediately without installing MySQL.

If your college specifically requires MySQL, the SQL schema can be adapted to MySQL and the Flask database layer can be switched to a MySQL connector.
