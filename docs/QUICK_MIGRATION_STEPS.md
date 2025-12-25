# Quick Migration Steps for Your Project

## What Are Migrations?

**Simple Explanation**: When you add new database tables (like `ScoringWeights`, `AIAuditLog`, `FairnessMetric`), migrations are scripts that tell your database "create these new tables with these columns."

Think of it like this:
- Your code says "I need a table called `scoring_weights`"
- Migrations say "Here's the SQL to create that table"
- The database executes it and creates the table

---

## Option 1: Quick Setup (SQLite - Development)

Since you're using SQLite, you can quickly create all tables with this Python script:

### Create `backend/create_tables.py`:

```python
"""
Quick script to create all database tables
Run this once to set up your database
"""
from app.database import Base, engine
from app import models  # Import all models

# Create all tables
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")
```

### Run it:

```bash
cd backend
python create_tables.py
```

**This will create all tables including the new ones you just added!**

---

## Option 2: Proper Migrations (Recommended for Production)

### Step 1: Initialize Alembic

```bash
cd backend
alembic init alembic
```

### Step 2: Configure Alembic

Edit `backend/alembic/env.py`:

1. **Update the database URL** (around line 20):
```python
# Find this line:
# sqlalchemy.url = ...

# Replace with:
from app.config import settings
sqlalchemy.url = settings.DATABASE_URL
```

2. **Import your models** (at the top of the file):
```python
from app.database import Base
from app import models  # This imports all your models
```

3. **Update target_metadata** (in the `run_migrations_online` function):
```python
target_metadata = Base.metadata
```

### Step 3: Create Migration

```bash
cd backend
alembic revision --autogenerate -m "Add adaptive learning and audit models"
```

### Step 4: Apply Migration

```bash
alembic upgrade head
```

---

## Which Should You Use?

- **Option 1 (Quick)**: If you're just developing locally and don't mind recreating the database
- **Option 2 (Migrations)**: If you want proper version control, team collaboration, or production deployment

---

## Verify It Worked

After running either option, check your database:

```python
# In Python shell
from app.database import SessionLocal
from app.models import ScoringWeights, AIAuditLog, FairnessMetric

db = SessionLocal()
# Try to query - if no error, tables exist!
weights = db.query(ScoringWeights).first()
print("✅ Tables created successfully!")
```

---

## Need Help?

If you get errors:
1. Make sure you're in the `backend` directory
2. Make sure your virtual environment is activated
3. Check that `alembic` is installed: `pip install alembic`

