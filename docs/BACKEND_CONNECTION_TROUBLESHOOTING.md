# Backend Connection Troubleshooting Guide

## Quick Checks

### 1. Is the Backend Server Running?

Check if port 8000 is in use:
```bash
# Windows PowerShell
netstat -ano | findstr :8000

# If you see output, the server is running
```

### 2. Start the Backend Server

If the server is not running, start it:

```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Test Backend Connection

Open your browser and go to:
- `http://localhost:8000/docs` - API documentation
- `http://localhost:8000/health` - Health check endpoint
- `http://localhost:8000/` - Root endpoint

### 4. Check Frontend Configuration

The frontend is configured to connect to `http://localhost:8000` by default.

Check `frontend/src/api/client.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

### 5. Common Issues

#### Issue: "No response from server"
**Solution**: 
- Make sure the backend server is running
- Check if port 8000 is not blocked by firewall
- Verify the backend is listening on `0.0.0.0:8000` not just `127.0.0.1:8000`

#### Issue: CORS errors
**Solution**: 
- Check `backend/app/config.py` - `CORS_ORIGINS` should include your frontend URL
- Default: `["http://localhost:3000", "http://localhost:5173"]`

#### Issue: Connection refused
**Solution**:
- Backend server is not running
- Wrong port number
- Firewall blocking the connection

#### Issue: 500 Internal Server Error
**Solution**:
- Check backend terminal for error messages
- Verify database connection
- Check if all required environment variables are set

### 6. Verify Backend is Working

Test with curl or browser:
```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# Root endpoint
curl http://localhost:8000/

# Should return API info
```

### 7. Check Backend Logs

When you start the backend, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 8. Database Connection Issues

If you see database errors:
- Make sure `smartrecruiter.db` exists in the `backend` directory
- Run `python create_tables.py` to create tables
- Check `backend/app/config.py` for `DATABASE_URL`

### 9. Port Already in Use

If port 8000 is already in use:
```bash
# Find the process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use a different port
uvicorn main:app --reload --port 8001
```

Then update frontend: `REACT_APP_API_URL=http://localhost:8001`

### 10. Network Issues

If running in different environments:
- **Same machine**: Use `http://localhost:8000`
- **Different machines**: Use `http://<backend-ip>:8000`
- **Docker**: Use service names or exposed ports

## Quick Start Commands

### Start Backend
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

### Start Frontend
```bash
cd frontend
npm start
```

### Check Both Are Running
- Backend: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

## Still Having Issues?

1. Check browser console for errors
2. Check backend terminal for errors
3. Verify both servers are running
4. Check network tab in browser DevTools
5. Verify CORS settings match your frontend URL

