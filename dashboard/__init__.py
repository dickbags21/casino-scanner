"""
Dashboard initialization
"""

from dashboard.database import get_db

# Initialize database
db = get_db()
db.init_db()


