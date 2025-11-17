"""
Unit tests for database models and operations
"""

import pytest
from datetime import datetime
from dashboard.database import Scan, ScanResult, Vulnerability, Target, Plugin as DBPlugin


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseModels:
    """Test database model creation and relationships"""
    
    def test_create_scan(self, db_session, sample_scan_data):
        """Test creating a scan record"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        assert scan.id is not None
        assert scan.scan_id == sample_scan_data["scan_id"]
        assert scan.name == sample_scan_data["name"]
        assert scan.scan_type == sample_scan_data["scan_type"]
        assert scan.status == sample_scan_data["status"]
        assert scan.progress == 0.0
        assert scan.created_at is not None
    
    def test_scan_relationships(self, db_session, sample_scan_data):
        """Test scan relationships with results and vulnerabilities"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        # Create related scan result
        result = ScanResult(
            scan_id=scan.id,
            result_type="signup_test",
            target_url="https://example.com",
            success=True,
            data={"test": "data"}
        )
        db_session.add(result)
        
        # Create related vulnerability
        vuln = Vulnerability(
            scan_id=scan.id,
            title="Test Vulnerability",
            description="Test description",
            severity="high",
            vulnerability_type="account_creation"
        )
        db_session.add(vuln)
        db_session.commit()
        
        # Test relationships
        assert len(scan.results) == 1
        assert len(scan.vulnerabilities) == 1
        assert scan.results[0].result_type == "signup_test"
        assert scan.vulnerabilities[0].title == "Test Vulnerability"
    
    def test_create_scan_result(self, db_session, sample_scan_data):
        """Test creating a scan result"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        result = ScanResult(
            scan_id=scan.id,
            result_type="browser",
            target_url="https://example.com",
            success=True,
            data={"key": "value"}
        )
        db_session.add(result)
        db_session.commit()
        
        assert result.id is not None
        assert result.scan_id == scan.id
        assert result.result_type == "browser"
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.timestamp is not None
    
    def test_create_vulnerability(self, db_session, sample_scan_data, sample_vulnerability_data):
        """Test creating a vulnerability record"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        vuln = Vulnerability(
            scan_id=scan.id,
            **sample_vulnerability_data
        )
        db_session.add(vuln)
        db_session.commit()
        
        assert vuln.id is not None
        assert vuln.scan_id == scan.id
        assert vuln.title == sample_vulnerability_data["title"]
        assert vuln.severity == sample_vulnerability_data["severity"]
        assert vuln.exploitability == sample_vulnerability_data["exploitability"]
        assert vuln.discovered_at is not None
    
    def test_create_target(self, db_session, sample_target_data):
        """Test creating a target record"""
        target = Target(**sample_target_data)
        db_session.add(target)
        db_session.commit()
        
        assert target.id is not None
        assert target.name == sample_target_data["name"]
        assert target.url == sample_target_data["url"]
        assert target.region == sample_target_data["region"]
        assert target.priority == sample_target_data["priority"]
        assert target.status == sample_target_data["status"]
        assert target.created_at is not None
    
    def test_create_plugin(self, db_session):
        """Test creating a plugin record"""
        plugin = DBPlugin(
            name="test_plugin",
            display_name="Test Plugin",
            description="A test plugin",
            version="1.0.0",
            enabled=True,
            config={"key": "value"}
        )
        db_session.add(plugin)
        db_session.commit()
        
        assert plugin.id is not None
        assert plugin.name == "test_plugin"
        assert plugin.display_name == "Test Plugin"
        assert plugin.enabled is True
        assert plugin.registered_at is not None
    
    def test_scan_status_transitions(self, db_session, sample_scan_data):
        """Test scan status transitions"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        # Test status updates
        scan.status = "running"
        scan.started_at = datetime.utcnow()
        db_session.commit()
        
        assert scan.status == "running"
        assert scan.started_at is not None
        
        scan.status = "completed"
        scan.completed_at = datetime.utcnow()
        scan.progress = 1.0
        db_session.commit()
        
        assert scan.status == "completed"
        assert scan.completed_at is not None
        assert scan.progress == 1.0
    
    def test_vulnerability_severity_levels(self, db_session, sample_scan_data):
        """Test different vulnerability severity levels"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        severities = ["critical", "high", "medium", "low", "info"]
        
        for severity in severities:
            vuln = Vulnerability(
                scan_id=scan.id,
                title=f"Test {severity} vulnerability",
                description="Test",
                severity=severity,
                vulnerability_type="test"
            )
            db_session.add(vuln)
        
        db_session.commit()
        
        # Verify all severities were created
        vulns = db_session.query(Vulnerability).filter_by(scan_id=scan.id).all()
        assert len(vulns) == len(severities)
        assert set(v.severity for v in vulns) == set(severities)


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseOperations:
    """Test database operations and queries"""
    
    def test_query_scans_by_status(self, db_session, sample_scan_data):
        """Test querying scans by status"""
        # Create scans with different statuses
        for status in ["pending", "running", "completed", "failed"]:
            scan_data = sample_scan_data.copy()
            scan_data["scan_id"] = f"test-scan-{status}"
            scan_data["status"] = status
            scan = Scan(**scan_data)
            db_session.add(scan)
        
        db_session.commit()
        
        # Query by status
        pending_scans = db_session.query(Scan).filter_by(status="pending").all()
        assert len(pending_scans) == 1
        assert pending_scans[0].status == "pending"
        
        completed_scans = db_session.query(Scan).filter_by(status="completed").all()
        assert len(completed_scans) == 1
        assert completed_scans[0].status == "completed"
    
    def test_query_vulnerabilities_by_severity(self, db_session, sample_scan_data):
        """Test querying vulnerabilities by severity"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        # Create vulnerabilities with different severities
        for severity in ["critical", "high", "medium"]:
            vuln = Vulnerability(
                scan_id=scan.id,
                title=f"{severity} vulnerability",
                description="Test",
                severity=severity,
                vulnerability_type="test"
            )
            db_session.add(vuln)
        
        db_session.commit()
        
        # Query high severity vulnerabilities
        high_vulns = db_session.query(Vulnerability).filter_by(severity="high").all()
        assert len(high_vulns) == 1
        assert high_vulns[0].severity == "high"
    
    def test_cascade_delete(self, db_session, sample_scan_data):
        """Test cascade delete of related records"""
        scan = Scan(**sample_scan_data)
        db_session.add(scan)
        db_session.commit()
        
        # Create related records
        result = ScanResult(
            scan_id=scan.id,
            result_type="test",
            target_url="https://example.com",
            success=True
        )
        db_session.add(result)
        
        vuln = Vulnerability(
            scan_id=scan.id,
            title="Test",
            description="Test",
            severity="high",
            vulnerability_type="test"
        )
        db_session.add(vuln)
        db_session.commit()
        
        # Delete scan (should cascade)
        db_session.delete(scan)
        db_session.commit()
        
        # Verify related records are deleted
        assert db_session.query(ScanResult).filter_by(id=result.id).first() is None
        assert db_session.query(Vulnerability).filter_by(id=vuln.id).first() is None

