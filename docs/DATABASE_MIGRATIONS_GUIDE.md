# Database Migrations Guide

## What are Database Migrations?

**Database migrations** are scripts that manage changes to your database schema (structure) over time. Think of them as version control for your database.

### Why Use Migrations?

1. **Track Changes**: Keep a history of all database structure changes
2. **Team Collaboration**: Everyone can apply the same changes to their database
3. **Deployment**: Easily update production databases without manual SQL
4. **Rollback**: Can undo changes if something goes wrong
5. **Consistency**: Ensures all environments (dev, staging, production) have the same structure

### Simple Analogy

Imagine you're building a house:
- **Models** (`models.py`) = The blueprint (what you want)
- **Migrations** = The construction steps (how to build it)
- **Database** = The actual house (what exists)

When you add a new room (new model/table), you need a migration to tell the database "add this room to the house."

---

## Your Project Setup

Your project uses:
- **Alembic** - The migration tool (already configured)
- **SQLAlchemy** - The ORM (Object-Relational Mapping)
- **SQLite** - Your database (default: `smartrecruiter.db`)

---

## Step-by-Step: Running Migrations

### Step 1: Initialize Alembic (First Time Only)

If you don't have an `alembic` folder yet, initialize it:

```bash
cd backend
alembic init alembic
```

This creates the migration folder structure.

### Step 2: Configure Alembic

Update `backend/alembic/env.py` to use your database URL from settings:

```python
# In alembic/env.py, find the line:
# sqlalchemy.url = ...

# Replace it with:
from app.config import settings
sqlalchemy.url = settings.DATABASE_URL
```

Also update `alembic/env.py` to import your models:

```python
# Add this import at the top
from app.database import Base
from app import models  # This imports all your models

# In the run_migrations_online function, update:
target_metadata = Base.metadata
```

### Step 3: Create a Migration

When you add new models (like `ScoringWeights`, `AIAuditLog`, `FairnessMetric`), create a migration:

```bash
cd backend
alembic revision --autogenerate -m "Add adaptive learning and audit models"
```

This will:
- Compare your current models with the database
- Generate a migration file with all the changes needed
- Save it in `backend/alembic/versions/`

### Step 4: Review the Migration

**IMPORTANT**: Always check the generated migration file before running it!

Open the file in `backend/alembic/versions/` and verify:
- ✅ Correct tables are being created
- ✅ Correct columns are being added
- ✅ No unintended changes

### Step 5: Apply the Migration

Run the migration to update your database:

```bash
cd backend
alembic upgrade head
```

This applies all pending migrations to your database.

---

## Common Migration Commands

### Check Current Database Version
```bash
alembic current
```

### See Migration History
```bash
alembic history
```

### Apply All Pending Migrations
```bash
alembic upgrade head
```

### Rollback One Migration
```bash
alembic downgrade -1
```

### Rollback to Specific Version
```bash
alembic downgrade <revision_id>
```

### Create Empty Migration (Manual)
```bash
alembic revision -m "Description of changes"
```

---

## For Your New Models

Since you just added these new models:
- `ScoringWeights`
- `AIAuditLog`
- `FairnessMetric`

You need to create a migration for them:

```bash
cd backend
alembic revision --autogenerate -m "Add adaptive learning and audit models"
alembic upgrade head
```

---

## Alternative: SQLite Auto-Create (Development Only)

If you're using SQLite and just want to quickly create tables without migrations (for development only), you can use:

```python
# In a Python script or Python shell
from app.database import Base, engine
from app import models

# Create all tables
Base.metadata.create_all(bind=engine)
```

**⚠️ Warning**: This doesn't track changes and won't work well in production or with teams. Use migrations for proper database management.

---

## Troubleshooting

### "Target database is not up to date"
```bash
# Check current version
alembic current

# Upgrade to latest
alembic upgrade head
```

### "Can't locate revision identified by..."
```bash
# Check what migrations exist
alembic history

# You may need to stamp the database
alembic stamp head
```

### Migration conflicts
If you have conflicts between team members:
1. Pull latest migrations
2. Run `alembic upgrade head`
3. If conflicts, resolve manually in migration files

---

## Best Practices

1. ✅ **Always review** generated migrations before applying
2. ✅ **Test migrations** on a copy of your database first
3. ✅ **Commit migrations** to version control (Git)
4. ✅ **Never edit** applied migrations (create new ones instead)
5. ✅ **Use descriptive names** for migrations
6. ✅ **Backup database** before major migrations

---

## Quick Reference

```bash
# Initialize (first time)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Check status
alembic current
alembic history
```

---

## Need Help?

If you encounter issues:
1. Check the error message carefully
2. Verify your database connection
3. Ensure all models are imported in `alembic/env.py`
4. Check that `Base.metadata` includes all your models

