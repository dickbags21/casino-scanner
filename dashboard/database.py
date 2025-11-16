"""
Database Layer for Casino Scanner Dashboard
SQLite models for scans, results, vulnerabilities, and targets
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from pathlib import Path
import json

Base = declarative_base()


class Scan(Base):
    """Scan job/task model"""
    __tablename__ = 'scans'
    
    id = Column(Integer, primary_key=True)
    scan_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    scan_type = Column(String, nullable=False)  # 'shodan', 'browser', 'account_creation', 'mobile_app', 'combined'
    region = Column(String)
    status = Column(String, default='pending')  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    plugin_name = Column(String)
    config = Column(JSON)  # Scan configuration as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Relationships
    results = relationship("ScanResult", back_populates="scan", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")


class ScanResult(Base):
    """Individual scan result model"""
    __tablename__ = 'scan_results'
    
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey('scans.id'), nullable=False)
    result_type = Column(String, nullable=False)  # 'shodan', 'signup_test', 'bonus_test', 'account_creation', 'mobile_app'
    target_url = Column(String)
    target_ip = Column(String)
    target_port = Column(Integer)
    success = Column(Boolean, default=False)
    data = Column(JSON)  # Full result data as JSON
    screenshot_path = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    scan = relationship("Scan", back_populates="results")


class Vulnerability(Base):
    """Vulnerability finding model"""
    __tablename__ = 'vulnerabilities'
    
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey('scans.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(String, nullable=False)  # 'critical', 'high', 'medium', 'low', 'info'
    vulnerability_type = Column(String)
    url = Column(String)
    ip = Column(String)
    port = Column(Integer)
    exploitability = Column(String)  # 'easy', 'medium', 'hard', 'theoretical'
    profit_potential = Column(String)
    technical_details = Column(JSON)
    proof_of_concept = Column(Text)
    mitigation = Column(Text)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    scan = relationship("Scan", back_populates="vulnerabilities")


class Target(Base):
    """Target management model"""
    __tablename__ = 'targets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String)
    ip = Column(String)
    region = Column(String)
    country_code = Column(String)
    tags = Column(JSON)  # List of tags
    priority = Column(Integer, default=5)  # 1-10
    status = Column(String, default='pending')  # 'pending', 'active', 'completed', 'archived'
    notes = Column(Text)
    last_scan_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Plugin(Base):
    """Plugin registry model"""
    __tablename__ = 'plugins'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    description = Column(Text)
    version = Column(String)
    enabled = Column(Boolean, default=True)
    config = Column(JSON)
    plugin_metadata = Column(JSON)  # Plugin metadata (renamed from 'metadata' to avoid conflict)
    registered_at = Column(DateTime, default=datetime.utcnow)


class Database:
    """Database manager"""
    
    def __init__(self, db_path: str = "dashboard/casino_scanner.db"):
        """
        Initialize database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.Session = Session
    
    def get_session(self):
        """Get database session"""
        return self.Session()
    
    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(self.engine)
    
    def reset_db(self):
        """Reset database (drop all tables)"""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)


# Global database instance
_db_instance = None

def get_db():
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

