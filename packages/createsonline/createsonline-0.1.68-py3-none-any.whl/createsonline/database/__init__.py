"""
CREATESONLINE Database Abstraction Layer

Pure Python database abstraction with zero external dependencies (except SQLAlchemy).
Clean API that hides SQLAlchemy complexity while providing AI-native features.
"""

from .abstraction import Database, Connection, Transaction, build_database_url
from .models import CreatesonlineModel, QueryBuilder
from .fields import (
    CreatesonlineField, StringField, IntegerField, FloatField,
    BooleanField, DateTimeField, TextField, JSONField,
    EmbeddingField, SlugField, EmailField, URLField
)
from .migrations import MigrationManager, Migration

__all__ = [
    # Core database
    'Database',
    'Connection',
    'Transaction',
    'build_database_url',

    # Models
    'CreatesonlineModel',
    'QueryBuilder',

    # Fields
    'CreatesonlineField',
    'StringField',
    'IntegerField',
    'FloatField',
    'BooleanField',
    'DateTimeField',
    'TextField',
    'JSONField',
    'EmbeddingField',
    'SlugField',
    'EmailField',
    'URLField',

    # Migrations
    'MigrationManager',
    'Migration',

    # Helper functions
    'get_database',
    'init_database',
    'init_db',
    'get_db',
    'Base',
]

# Global database instance
_database_instance = None
Base = None  # Will be set by init_database()

def get_database() -> Database:
    """Get global database instance"""
    global _database_instance
    if _database_instance is None:
        _database_instance = Database()
    return _database_instance

def init_database(database_url: str = None, **kwargs) -> Database:
    """
    Initialize database with custom configuration

    Args:
        database_url: Database connection URL
        **kwargs: Additional database configuration

    Returns:
        Database instance
    """
    global _database_instance, Base
    _database_instance = Database(database_url=database_url, **kwargs)

    # Export Base globally
    if hasattr(_database_instance, 'Base'):
        Base = _database_instance.Base

    return _database_instance

def init_db(database_url: str = None, create_tables: bool = True, **kwargs):
    """
    Initialize database and optionally create all tables (Django-style)

    Args:
        database_url: Database connection URL
        create_tables: If True, creates all tables automatically
        **kwargs: Additional database configuration

    Returns:
        Database instance
    """
    db = init_database(database_url=database_url, **kwargs)

    if create_tables and hasattr(db, 'Base') and hasattr(db, 'engine'):
        # Create all tables from registered models
        print("🗄️  Creating database tables...")
        db.Base.metadata.create_all(bind=db.engine)
        print("✅ Database tables created successfully")

    return db

def get_db():
    """
    Get database session (for dependency injection)

    Yields:
        Database session
    """
    db = get_database()
    session = db.get_session()
    try:
        yield session
    finally:
        if hasattr(session, 'close'):
            session.close()