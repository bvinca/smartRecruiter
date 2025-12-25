# How to Start the Backend Server

## Quick Start

The backend server needs to be running for the frontend to work. Here's how to start it:

### Step 1: Open a Terminal/PowerShell

Navigate to the backend directory:
```bash
cd D:\york\smartRecruiter\smartRecruiter\backend
```

### Step 2: Activate Virtual Environment

```bash
.\venv\Scripts\Activate.ps1
```

### Step 3: Start the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 4: Verify It's Running

Open your browser and go to:
- `http://localhost:8000/docs` - Should show API documentation
- `http://localhost:8000/health` - Should return `{"status":"healthy"}`

## Keep the Terminal Open

**Important**: Keep the terminal window open while the backend is running. Closing it will stop the server.

## Troubleshooting

### Port Already in Use

If you get an error that port 8000 is already in use:

1. Find what's using it:
```bash
netstat -ano | findstr :8000
```

2. Kill the process (replace PID with the number from step 1):
```bash
taskkill /PID <PID> /F
```

3. Start the server again

### Module Not Found Errors

Make sure you're in the backend directory and the virtual environment is activated:
```bash
cd backend
.\venv\Scripts\Activate.ps1
```

### Database Errors

If you see database errors, make sure the database file exists:
```bash
python create_tables.py
```

## Running Both Frontend and Backend

You need **two terminal windows**:

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## Auto-Reload

The `--reload` flag means the server will automatically restart when you change code files. This is useful during development.

